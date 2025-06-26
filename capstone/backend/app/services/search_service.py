"""
Legal Document Semantic Search Service

This service provides advanced semantic search capabilities for legal documents using 
vector embeddings, hybrid search, and caching for optimal performance.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import hashlib
import json
import re

from app.services.embedding_service import LegalEmbeddingService
from app.services.document_storage import DocumentStorageService
from app.core.database import supabase

logger = logging.getLogger(__name__)


class AdvancedLegalSearchService:
    """Enhanced service for semantic search in legal documents with caching and advanced features"""
    
    def __init__(self):
        self.embedding_service = LegalEmbeddingService()
        self.document_storage = DocumentStorageService()
        
        # Enhanced legal terminology patterns
        self.legal_query_patterns = {
            'obligations': ['must', 'shall', 'required to', 'obligated to', 'duty to', 'responsible for'],
            'rights': ['right to', 'entitled to', 'may', 'permission to', 'authorized to'],
            'definitions': ['means', 'defined as', 'refers to', 'definition', 'includes', 'excludes'],
            'termination': ['terminate', 'end', 'expire', 'dissolution', 'cancellation', 'breach'],
            'liability': ['liable', 'responsible', 'damages', 'compensation', 'indemnification'],
            'confidentiality': ['confidential', 'non-disclosure', 'proprietary', 'secret', 'private'],
            'payment': ['payment', 'fee', 'compensation', 'remuneration', 'salary', 'invoice'],
            'dispute': ['dispute', 'disagreement', 'arbitration', 'litigation', 'mediation'],
            'intellectual_property': ['copyright', 'trademark', 'patent', 'trade secret', 'IP'],
            'force_majeure': ['force majeure', 'act of god', 'unforeseeable', 'beyond control'],
            'warranties': ['warrant', 'guarantee', 'represent', 'assure', 'promise'],
            'amendments': ['amend', 'modify', 'change', 'update', 'revise', 'alter']
        }
        
        # Legal entity patterns
        self.legal_entities = {
            'parties': ['party', 'parties', 'client', 'customer', 'vendor', 'contractor'],
            'documents': ['agreement', 'contract', 'addendum', 'amendment', 'schedule'],
            'periods': ['term', 'period', 'duration', 'expiry', 'renewal'],
            'locations': ['jurisdiction', 'venue', 'governing law', 'state', 'country']
        }
        
        # Cache for search results (in-memory for demo, use Redis in production)
        self._search_cache = {}
        self._cache_ttl = timedelta(minutes=30)
    
    def _generate_cache_key(self, query: str, filters: Dict[str, Any]) -> str:
        """Generate a cache key for search results"""
        cache_data = {
            'query': query.lower().strip(),
            'filters': sorted(filters.items()) if filters else []
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached search result if still valid"""
        if cache_key in self._search_cache:
            cached_data = self._search_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < self._cache_ttl:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_data['result']
            else:
                # Remove expired cache entry
                del self._search_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache search result with timestamp"""
        self._search_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.utcnow()
        }
        logger.info(f"Cached result for key: {cache_key}")
    
    def _extract_legal_entities(self, query: str) -> List[str]:
        """Extract legal entities and concepts from query"""
        entities = []
        query_lower = query.lower()
        
        for category, terms in {**self.legal_query_patterns, **self.legal_entities}.items():
            for term in terms:
                if term in query_lower:
                    entities.append(f"{category}:{term}")
        
        return entities
    
    def _expand_legal_query(self, query: str) -> str:
        """Advanced legal query expansion with synonyms and related terms"""
        expanded_terms = []
        query_lower = query.lower()
        
        # Find matching legal patterns and expand
        for category, terms in self.legal_query_patterns.items():
            for term in terms:
                if term in query_lower:
                    # Add related terms from the same category
                    related_terms = [t for t in terms if t != term][:3]  # Top 3 related terms
                    expanded_terms.extend(related_terms)
        
        # Add legal context
        legal_context = "legal document contract agreement clause"
        
        # Combine original query with expansions
        if expanded_terms:
            expansion = " ".join(set(expanded_terms))
            return f"{query} {expansion} {legal_context}"
        else:
            return f"{query} {legal_context}"
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand legal intent and suggest search strategies"""
        query_lower = query.lower()
        intent = {
            'type': 'general',
            'confidence': 0.5,
            'suggested_filters': [],
            'legal_concepts': []
        }
        
        # Question patterns
        question_patterns = {
            'what': {'type': 'definition', 'confidence': 0.8},
            'how': {'type': 'procedure', 'confidence': 0.8},
            'when': {'type': 'temporal', 'confidence': 0.8},
            'who': {'type': 'responsibility', 'confidence': 0.8},
            'where': {'type': 'jurisdiction', 'confidence': 0.8},
            'why': {'type': 'rationale', 'confidence': 0.7}
        }
        
        for question_word, intent_info in question_patterns.items():
            if query_lower.startswith(question_word):
                intent.update(intent_info)
                break
        
        # Legal concept detection
        for category, terms in self.legal_query_patterns.items():
            for term in terms:
                if term in query_lower:
                    intent['legal_concepts'].append(category)
                    intent['confidence'] = min(intent['confidence'] + 0.1, 1.0)
        
        # Suggest chunk type filters based on intent
        if intent['type'] == 'definition':
            intent['suggested_filters'].append('definition')
        elif intent['type'] in ['procedure', 'temporal']:
            intent['suggested_filters'].extend(['clause', 'paragraph'])
        
        return intent
    
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
    
    async def advanced_semantic_search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        enable_caching: bool = True,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced semantic search with caching, query analysis, and suggestions
        
        Args:
            query: Search query
            document_ids: Optional filter by document IDs
            chunk_types: Optional filter by chunk types
            user_id: User ID for access control
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            enable_caching: Whether to use result caching
            include_suggestions: Whether to include search suggestions
            
        Returns:
            Enhanced search results with analysis and suggestions
        """
        try:
            start_time = datetime.utcnow()
            
            # Generate cache key
            filters = {
                'document_ids': document_ids,
                'chunk_types': chunk_types,
                'user_id': user_id,
                'limit': limit,
                'similarity_threshold': similarity_threshold
            }
            cache_key = self._generate_cache_key(query, filters)
            
            # Check cache first
            if enable_caching:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            
            # Analyze query intent
            query_intent = self._analyze_query_intent(query)
            
            # Extract legal entities
            legal_entities = self._extract_legal_entities(query)
            
            # Expand query with legal context
            expanded_query = self._expand_legal_query(query)
            
            # Apply intent-based filters
            if query_intent['suggested_filters'] and not chunk_types:
                chunk_types = query_intent['suggested_filters']
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_query_embedding(expanded_query)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return self._empty_search_result(query, "Failed to generate query embedding")
            
            # Get user's accessible documents if user_id provided
            if user_id and not document_ids:
                accessible_docs = await self._get_accessible_documents(user_id)
                document_ids = [doc['id'] for doc in accessible_docs]
            
            # Perform enhanced vector search
            vector_results = await self._enhanced_vector_search(
                query_embedding=query_embedding,
                original_query=query,
                document_ids=document_ids,
                chunk_types=chunk_types,
                similarity_threshold=similarity_threshold,
                limit=limit
            )
            
            # Perform hybrid search for better recall
            hybrid_results = await self._perform_keyword_search(
                query=query,
                document_ids=document_ids,
                chunk_types=chunk_types,
                limit=limit//2
            )
            
            # Combine and rerank results
            combined_results = self._combine_and_rerank_results(
                vector_results, 
                hybrid_results, 
                query_intent,
                limit
            )
            
            # Generate search suggestions if requested
            suggestions = []
            if include_suggestions:
                suggestions = await self._generate_search_suggestions(
                    query, 
                    combined_results, 
                    legal_entities
                )
            
            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Prepare final result
            result = {
                'query': query,
                'expanded_query': expanded_query,
                'results': combined_results,
                'total_results': len(combined_results),
                'search_time': search_time,
                'query_intent': query_intent,
                'legal_entities': legal_entities,
                'suggestions': suggestions,
                'filters_applied': {
                    'document_ids': document_ids,
                    'chunk_types': chunk_types,
                    'similarity_threshold': similarity_threshold
                }
            }
            
            # Cache the result
            if enable_caching:
                self._cache_result(cache_key, result)
            
            # Log search analytics
            await self._log_search_analytics(
                user_id=user_id,
                query=query,
                results_count=len(combined_results),
                search_time=search_time,
                query_type='advanced_semantic'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced semantic search: {str(e)}")
            return self._empty_search_result(query, str(e))
    
    async def multi_document_comparison(
        self,
        query: str,
        document_ids: List[str],
        user_id: Optional[str] = None,
        comparison_type: str = 'similarity'
    ) -> Dict[str, Any]:
        """
        Compare multiple documents for similarities and differences
        
        Args:
            query: Comparison query or concept
            document_ids: List of document IDs to compare
            user_id: User ID for access control
            comparison_type: Type of comparison ('similarity', 'difference', 'coverage')
            
        Returns:
            Comparison results with cross-document analysis
        """
        try:
            start_time = datetime.utcnow()
            
            if len(document_ids) < 2:
                return {
                    'error': 'At least 2 documents required for comparison',
                    'documents_provided': len(document_ids)
                }
            
            # Get document metadata
            documents_info = await self._get_documents_info(document_ids, user_id)
            
            # Perform search in each document separately
            document_results = {}
            
            for doc_id in document_ids:
                doc_search = await self.advanced_semantic_search(
                    query=query,
                    document_ids=[doc_id],
                    user_id=user_id,
                    limit=10,
                    enable_caching=False
                )
                document_results[doc_id] = doc_search['results']
            
            # Analyze cross-document patterns
            comparison_analysis = self._analyze_cross_document_patterns(
                document_results, 
                documents_info, 
                comparison_type
            )
            
            search_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'query': query,
                'comparison_type': comparison_type,
                'documents': documents_info,
                'document_results': document_results,
                'comparison_analysis': comparison_analysis,
                'search_time': search_time
            }
            
        except Exception as e:
            logger.error(f"Error in multi-document comparison: {str(e)}")
            return {'error': str(e)}
    
    async def _enhanced_vector_search(
        self,
        query_embedding: List[float],
        original_query: str,
        document_ids: Optional[List[str]],
        chunk_types: Optional[List[str]],
        similarity_threshold: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Enhanced vector search with better ranking"""
        try:
            # Use the existing embedding service method
            results = await self.embedding_service.find_similar_chunks(
                query_embedding=query_embedding,
                document_ids=document_ids,
                chunk_types=chunk_types,
                similarity_threshold=similarity_threshold,
                limit=limit * 2  # Get more results for reranking
            )
            
            # Enhanced ranking with query-specific factors
            enhanced_results = []
            for result in results:
                # Calculate enhanced score
                enhanced_score = self._calculate_enhanced_score(
                    result, 
                    original_query, 
                    query_embedding
                )
                
                result['enhanced_score'] = enhanced_score
                result['ranking_factors'] = {
                    'similarity_score': result.get('similarity_score', 0),
                    'query_term_overlap': self._calculate_query_overlap(result['content'], original_query),
                    'chunk_type_bonus': self._get_chunk_type_bonus(result.get('chunk_type', '')),
                    'document_relevance': self._calculate_document_relevance(result)
                }
                
                enhanced_results.append(result)
            
            # Sort by enhanced score and limit results
            enhanced_results.sort(key=lambda x: x['enhanced_score'], reverse=True)
            return enhanced_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in enhanced vector search: {str(e)}")
            return []
    
    def _calculate_enhanced_score(
        self, 
        result: Dict[str, Any], 
        original_query: str, 
        query_embedding: List[float]
    ) -> float:
        """Calculate enhanced ranking score combining multiple factors"""
        base_similarity = result.get('similarity_score', 0)
        query_overlap = self._calculate_query_overlap(result['content'], original_query)
        chunk_bonus = self._get_chunk_type_bonus(result.get('chunk_type', ''))
        doc_relevance = self._calculate_document_relevance(result)
        
        # Weighted combination
        enhanced_score = (
            base_similarity * 0.4 +
            query_overlap * 0.3 +
            chunk_bonus * 0.15 +
            doc_relevance * 0.15
        )
        
        return min(enhanced_score, 1.0)
    
    def _calculate_query_overlap(self, content: str, query: str) -> float:
        """Calculate overlap between content and query terms"""
        try:
            content_lower = content.lower()
            query_terms = set(query.lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            query_terms = query_terms - stop_words
            
            if not query_terms:
                return 0.0
            
            overlap_count = sum(1 for term in query_terms if term in content_lower)
            return overlap_count / len(query_terms)
            
        except Exception:
            return 0.0
    
    def _get_chunk_type_bonus(self, chunk_type: str) -> float:
        """Get bonus score based on chunk type relevance"""
        bonuses = {
            'clause': 0.9,
            'definition': 0.8,
            'heading': 0.7,
            'paragraph': 0.6,
            'list_item': 0.5
        }
        return bonuses.get(chunk_type, 0.5)
    
    def _calculate_document_relevance(self, result: Dict[str, Any]) -> float:
        """Calculate document-level relevance score"""
        # Simple implementation - can be enhanced with document metadata
        doc_title = result.get('document_title', '')
        doc_type = result.get('document_type', '')
        
        relevance = 0.5  # Base score
        
        # Boost for legal document types
        if doc_type in ['contract', 'agreement', 'policy']:
            relevance += 0.2
        
        # Boost for descriptive titles
        if len(doc_title) > 10:
            relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _combine_and_rerank_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        query_intent: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Combine vector and keyword results with intelligent reranking"""
        combined = {}
        
        # Add vector results with high weight
        for result in vector_results:
            chunk_id = result.get('id')
            if chunk_id:
                combined[chunk_id] = result
                combined[chunk_id]['source'] = 'vector'
                combined[chunk_id]['combined_score'] = result.get('enhanced_score', 0.5)
        
        # Add keyword results with lower weight, boost if not in vector results
        for result in keyword_results:
            chunk_id = result.get('id')
            if chunk_id:
                if chunk_id in combined:
                    # Boost existing result
                    combined[chunk_id]['combined_score'] += 0.2
                    combined[chunk_id]['source'] = 'hybrid'
                else:
                    # Add new result with keyword weight
                    result['source'] = 'keyword'
                    result['combined_score'] = result.get('keyword_rank', 0.3)
                    combined[chunk_id] = result
        
        # Apply intent-based boosting
        for chunk_id, result in combined.items():
            intent_boost = self._calculate_intent_boost(result, query_intent)
            combined[chunk_id]['combined_score'] += intent_boost
            combined[chunk_id]['combined_score'] = min(combined[chunk_id]['combined_score'], 1.0)
        
        # Sort by combined score and limit
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_results[:limit]
    
    def _calculate_intent_boost(self, result: Dict[str, Any], query_intent: Dict[str, Any]) -> float:
        """Calculate boost based on query intent matching"""
        boost = 0.0
        
        content = result.get('content', '').lower()
        intent_type = query_intent.get('type', 'general')
        
        # Intent-specific boosting
        if intent_type == 'definition' and 'definition' in result.get('chunk_type', ''):
            boost += 0.2
        elif intent_type == 'procedure' and any(word in content for word in ['step', 'process', 'procedure']):
            boost += 0.15
        elif intent_type == 'temporal' and any(word in content for word in ['date', 'time', 'period', 'duration']):
            boost += 0.15
        
        # Legal concept boosting
        for concept in query_intent.get('legal_concepts', []):
            if concept in content:
                boost += 0.1
        
        return min(boost, 0.3)  # Cap the boost
    
    async def _generate_search_suggestions(
        self,
        query: str,
        results: List[Dict[str, Any]],
        legal_entities: List[str]
    ) -> List[str]:
        """Generate intelligent search suggestions based on results and context"""
        suggestions = []
        
        try:
            # Extract common terms from top results
            if results:
                top_content = " ".join([r.get('content', '') for r in results[:3]])
                content_words = set(re.findall(r'\b\w+\b', top_content.lower()))
                
                # Filter for meaningful legal terms
                legal_terms = []
                for word in content_words:
                    if len(word) > 4 and word not in ['shall', 'party', 'agreement']:
                        legal_terms.append(word)
                
                # Create suggestions based on legal patterns
                for category, terms in self.legal_query_patterns.items():
                    for term in terms:
                        if term in top_content.lower() and term not in query.lower():
                            suggestions.append(f"{query} {term}")
            
            # Add entity-based suggestions
            for entity in legal_entities[:3]:
                if ':' in entity:
                    concept, term = entity.split(':', 1)
                    if term not in query.lower():
                        suggestions.append(f"{query} {term}")
            
            # Add common legal search patterns
            common_patterns = [
                f"what are {query}",
                f"how to {query}",
                f"{query} obligations",
                f"{query} requirements",
                f"{query} definition"
            ]
            
            suggestions.extend(common_patterns)
            
            # Remove duplicates and limit
            suggestions = list(set(suggestions))[:5]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
        
        return suggestions
    
    async def _get_documents_info(self, document_ids: List[str], user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get document metadata for given IDs"""
        try:
            query = supabase.table("documents").select("*").in_("id", document_ids)
            
            if user_id:
                query = query.eq("uploaded_by", user_id)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting documents info: {str(e)}")
            return []
    
    def _analyze_cross_document_patterns(
        self,
        document_results: Dict[str, List[Dict[str, Any]]],
        documents_info: List[Dict[str, Any]],
        comparison_type: str
    ) -> Dict[str, Any]:
        """Analyze patterns across multiple documents"""
        analysis = {
            'comparison_type': comparison_type,
            'document_count': len(document_results),
            'similarities': [],
            'differences': [],
            'coverage_analysis': {}
        }
        
        try:
            # Find similar content across documents
            all_contents = {}
            for doc_id, results in document_results.items():
                all_contents[doc_id] = [r.get('content', '') for r in results]
            
            # Simple similarity analysis
            if comparison_type == 'similarity':
                analysis['similarities'] = self._find_similar_content(all_contents)
            elif comparison_type == 'difference':
                analysis['differences'] = self._find_different_content(all_contents)
            elif comparison_type == 'coverage':
                analysis['coverage_analysis'] = self._analyze_coverage(all_contents, documents_info)
            
        except Exception as e:
            logger.error(f"Error analyzing cross-document patterns: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _find_similar_content(self, all_contents: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Find similar content across documents"""
        similarities = []
        
        doc_ids = list(all_contents.keys())
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                doc1, doc2 = doc_ids[i], doc_ids[j]
                
                # Simple word overlap analysis
                content1 = " ".join(all_contents[doc1]).lower()
                content2 = " ".join(all_contents[doc2]).lower()
                
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                overlap = words1.intersection(words2)
                similarity_score = len(overlap) / max(len(words1.union(words2)), 1)
                
                if similarity_score > 0.3:  # Threshold for similarity
                    similarities.append({
                        'documents': [doc1, doc2],
                        'similarity_score': similarity_score,
                        'common_terms': list(overlap)[:10]  # Top 10 common terms
                    })
        
        return similarities
    
    def _find_different_content(self, all_contents: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Find unique content in each document"""
        differences = []
        
        # Get unique terms for each document
        for doc_id, contents in all_contents.items():
            doc_words = set(" ".join(contents).lower().split())
            
            # Find words unique to this document
            other_words = set()
            for other_id, other_contents in all_contents.items():
                if other_id != doc_id:
                    other_words.update(" ".join(other_contents).lower().split())
            
            unique_words = doc_words - other_words
            
            if unique_words:
                differences.append({
                    'document': doc_id,
                    'unique_terms': list(unique_words)[:20],  # Top 20 unique terms
                    'uniqueness_score': len(unique_words) / max(len(doc_words), 1)
                })
        
        return differences
    
    def _analyze_coverage(self, all_contents: Dict[str, List[str]], documents_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topic coverage across documents"""
        coverage = {
            'total_documents': len(all_contents),
            'topic_distribution': {},
            'coverage_gaps': []
        }
        
        # Simple topic analysis based on legal concepts
        for concept, terms in self.legal_query_patterns.items():
            concept_coverage = {}
            
            for doc_id, contents in all_contents.items():
                doc_text = " ".join(contents).lower()
                concept_mentions = sum(1 for term in terms if term in doc_text)
                concept_coverage[doc_id] = concept_mentions
            
            coverage['topic_distribution'][concept] = concept_coverage
        
        return coverage
    
    async def _log_search_analytics(
        self,
        user_id: Optional[str],
        query: str,
        results_count: int,
        search_time: float,
        query_type: str
    ) -> None:
        """Log search analytics for performance tracking"""
        try:
            analytics_data = {
                'user_id': user_id,
                'query': query,
                'query_type': query_type,
                'results_count': results_count,
                'search_time': search_time,
                'created_at': datetime.utcnow().isoformat()
            }
            
            supabase.table("search_analytics").insert(analytics_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging search analytics: {str(e)}")
    
    def _empty_search_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """Return empty search result with error information"""
        return {
            'query': query,
            'results': [],
            'total_results': 0,
            'search_time': 0,
            'error': error_message,
            'suggestions': []
        }
