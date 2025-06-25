"""
Legal Document Semantic Search Service

This service provides semantic search capabilities for legal documents using 
vector embeddings and hybrid search approaches.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

from app.services.embedding_service import LegalEmbeddingService
from app.services.document_storage import DocumentStorageService
from app.core.database import supabase

logger = logging.getLogger(__name__)


class LegalSearchService:
    """Service for semantic search in legal documents"""
    
    def __init__(self):
        self.embedding_service = LegalEmbeddingService()
        self.document_storage = DocumentStorageService()
        
        # Legal search enhancement patterns
        self.legal_query_patterns = {
            'obligations': ['must', 'shall', 'required to', 'obligated to', 'duty to'],
            'rights': ['right to', 'entitled to', 'may', 'permission to'],
            'definitions': ['means', 'defined as', 'refers to', 'definition'],
            'termination': ['terminate', 'end', 'expire', 'dissolution'],
            'liability': ['liable', 'responsible', 'damages', 'compensation'],
            'confidentiality': ['confidential', 'non-disclosure', 'proprietary'],
            'payment': ['payment', 'fee', 'compensation', 'remuneration'],
            'dispute': ['dispute', 'disagreement', 'arbitration', 'litigation']
        }
    
    async def semantic_search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        include_hybrid: bool = True
    ) -> Dict[str, Any]:
        """
        Perform semantic search across legal documents
        
        Args:
            query: Search query
            document_ids: Optional filter by document IDs
            chunk_types: Optional filter by chunk types
            user_id: User ID for access control
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            include_hybrid: Whether to include keyword search results
            
        Returns:
            Search results with metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Enhance query for legal context
            enhanced_query = self._enhance_legal_query(query)
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_query_embedding(enhanced_query)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return self._empty_search_result(query, "Failed to generate query embedding")
            
            # Get user's accessible documents if user_id provided
            if user_id and not document_ids:
                accessible_docs = await self._get_accessible_documents(user_id)
                document_ids = [doc['id'] for doc in accessible_docs]
            
            # Perform vector similarity search
            vector_results = await self.embedding_service.find_similar_chunks(
                query_embedding=query_embedding,
                document_ids=document_ids,
                chunk_types=chunk_types,
                similarity_threshold=similarity_threshold,
                limit=limit
            )
            
            # Perform hybrid search if enabled
            hybrid_results = []
            if include_hybrid:
                hybrid_results = await self._perform_keyword_search(
                    query=query,
                    document_ids=document_ids,
                    chunk_types=chunk_types,
                    limit=limit//2  # Use half the limit for keyword results
                )
            
            # Combine and rank results
            combined_results = self._combine_search_results(vector_results, hybrid_results)
            
            # Add legal context analysis
            legal_analysis = self._analyze_legal_context(query, combined_results)
            
            end_time = datetime.utcnow()
            search_time = (end_time - start_time).total_seconds()
            
            return {
                "query": query,
                "enhanced_query": enhanced_query,
                "total_results": len(combined_results),
                "results": combined_results[:limit],
                "legal_analysis": legal_analysis,
                "search_metadata": {
                    "search_time": search_time,
                    "vector_results": len(vector_results),
                    "keyword_results": len(hybrid_results),
                    "similarity_threshold": similarity_threshold,
                    "timestamp": start_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return self._empty_search_result(query, str(e))
    
    def _enhance_legal_query(self, query: str) -> str:
        """Enhance query with legal context and terminology"""
        query_lower = query.lower()
        
        # Identify legal categories
        identified_categories = []
        for category, patterns in self.legal_query_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                identified_categories.append(category)
        
        # Add legal context
        if identified_categories:
            category_context = f"Legal categories: {', '.join(identified_categories)}. "
        else:
            category_context = "General legal query. "
        
        enhanced_query = f"{category_context}Legal document search: {query}"
        
        return enhanced_query
    
    async def _get_accessible_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get documents accessible to the user"""
        try:
            result = supabase.table("documents").select("id, title, document_type").eq(
                "uploaded_by", user_id
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting accessible documents: {str(e)}")
            return []
    
    async def _perform_keyword_search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search as complement to vector search"""
        try:
            # Build full-text search query
            search_query = supabase.table("document_chunks").select(
                "*, documents!inner(title, filename)"
            ).text_search("content", query, config="english")
            
            # Apply filters
            if document_ids:
                search_query = search_query.in_("document_id", document_ids)
            
            if chunk_types:
                search_query = search_query.in_("chunk_type", chunk_types)
            
            result = search_query.limit(limit).execute()
            
            # Add keyword match score
            keyword_results = []
            for chunk in result.data if result.data else []:
                # Simple keyword matching score
                query_words = set(query.lower().split())
                content_words = set(chunk['content'].lower().split())
                
                match_score = len(query_words.intersection(content_words)) / len(query_words)
                
                chunk['similarity_score'] = match_score
                chunk['search_type'] = 'keyword'
                keyword_results.append(chunk)
            
            return keyword_results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []
    
    def _combine_search_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine and deduplicate vector and keyword search results"""
        
        # Mark vector results
        for result in vector_results:
            result['search_type'] = 'vector'
        
        # Combine results
        all_results = vector_results + keyword_results
        
        # Deduplicate by chunk ID
        seen_ids = set()
        unique_results = []
        
        for result in all_results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        # Sort by similarity score (descending)
        unique_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return unique_results
    
    def _analyze_legal_context(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze legal context of search results"""
        
        if not results:
            return {"analysis": "No results found for analysis"}
        
        # Analyze chunk types
        chunk_type_distribution = {}
        document_distribution = {}
        
        for result in results:
            chunk_type = result.get('chunk_type', 'unknown')
            doc_id = result.get('document_id', 'unknown')
            
            chunk_type_distribution[chunk_type] = chunk_type_distribution.get(chunk_type, 0) + 1
            document_distribution[doc_id] = document_distribution.get(doc_id, 0) + 1
        
        # Identify dominant legal concepts
        query_lower = query.lower()
        identified_concepts = []
        
        for concept, patterns in self.legal_query_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                identified_concepts.append(concept)
        
        # Analyze result relevance
        high_relevance = [r for r in results if r.get('similarity_score', 0) > 0.8]
        medium_relevance = [r for r in results if 0.6 <= r.get('similarity_score', 0) <= 0.8]
        
        return {
            "identified_concepts": identified_concepts,
            "chunk_type_distribution": chunk_type_distribution,
            "document_distribution": document_distribution,
            "relevance_analysis": {
                "high_relevance_count": len(high_relevance),
                "medium_relevance_count": len(medium_relevance),
                "total_results": len(results)
            },
            "recommendation": self._generate_search_recommendation(results, identified_concepts)
        }
    
    def _generate_search_recommendation(
        self, 
        results: List[Dict[str, Any]], 
        concepts: List[str]
    ) -> str:
        """Generate search recommendation based on results"""
        
        if not results:
            return "No relevant content found. Try broadening your search terms or checking document access permissions."
        
        if len(results) == 1:
            return "Single result found. Consider expanding your search to find related clauses or provisions."
        
        # Analyze result quality
        high_quality = len([r for r in results if r.get('similarity_score', 0) > 0.8])
        
        if high_quality > 3:
            return "Multiple highly relevant results found. Review the top results for comprehensive coverage."
        elif high_quality > 0:
            return "Some relevant results found. Consider refining your query for more specific results."
        else:
            return "Results found but with lower relevance. Consider using different legal terminology or synonyms."
    
    def _empty_search_result(self, query: str, error: str) -> Dict[str, Any]:
        """Return empty search result with error"""
        return {
            "query": query,
            "total_results": 0,
            "results": [],
            "error": error,
            "search_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "search_time": 0
            }
        }
    
    async def search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Generate search suggestions based on partial query"""
        try:
            # Simple implementation - can be enhanced with ML models
            suggestions = []
            
            partial_lower = partial_query.lower()
            
            # Add legal concept suggestions
            for concept, patterns in self.legal_query_patterns.items():
                for pattern in patterns:
                    if pattern.startswith(partial_lower) or partial_lower in pattern:
                        suggestions.append(f"Find {concept} related to {partial_query}")
            
            # Add common legal queries
            common_queries = [
                f"What are the {partial_query} obligations?",
                f"Define {partial_query} in this contract",
                f"Find {partial_query} clauses",
                f"What happens if {partial_query}?",
                f"Rights and duties regarding {partial_query}"
            ]
            
            suggestions.extend(common_queries)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating search suggestions: {str(e)}")
            return []
    
    async def get_search_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get search analytics and insights"""
        try:
            # This would typically be stored in a search_logs table
            # For now, return embedding statistics
            
            embedding_stats = await self.embedding_service.get_embedding_stats()
            
            analytics = {
                "embedding_coverage": embedding_stats.get("embedding_coverage", 0),
                "total_searchable_chunks": embedding_stats.get("embedded_chunks", 0),
                "search_readiness": "Ready" if embedding_stats.get("embedded_chunks", 0) > 0 else "Not Ready",
                "recommendations": []
            }
            
            # Add recommendations
            if embedding_stats.get("embedded_chunks", 0) == 0:
                analytics["recommendations"].append("Generate embeddings for documents to enable semantic search")
            
            if embedding_stats.get("embedding_coverage", 0) < 100:
                analytics["recommendations"].append("Some documents are not fully embedded - consider reprocessing")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {str(e)}")
            return {"error": str(e)}
