"""
Legal Document RAG (Retrieval-Augmented Generation) Service

This service provides AI-powered question answering capabilities for legal documents
using Google Gemini with retrieved context from semantic search.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

import google.generativeai as genai
from app.core.config import settings
from app.services.search_service import AdvancedLegalSearchService
from app.services.embedding_service import LegalEmbeddingService
from app.core.database import supabase

logger = logging.getLogger(__name__)


class LegalRAGService:
    """Service for legal document question answering using RAG"""
    
    def __init__(self):
        # Initialize Google Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('Gemini-2.0-Flash')  # Use Flash for reasoning
        self.search_service = AdvancedLegalSearchService()
        
        # Legal domain prompts
        self.system_prompt = """
        You are a legal document analysis AI assistant. Your role is to help legal professionals 
        understand and analyze legal documents by providing accurate, well-sourced answers.

        IMPORTANT GUIDELINES:
        1. Only answer based on the provided document context
        2. Always cite specific document sections and page numbers when available
        3. If information is not in the provided context, clearly state this
        4. Use precise legal terminology and maintain professional tone
        5. Highlight potential ambiguities or areas needing human legal review
        6. Never provide legal advice - only document analysis and interpretation
        7. Include disclaimers about the need for professional legal review

        RESPONSE FORMAT:
        - Direct answer based on documents
        - Relevant citations with document names and locations
        - Legal analysis and interpretation
        - Potential implications or considerations
        - Disclaimer about professional legal review need
        """
        
        self.citation_prompt = """
        When citing sources, use this format:
        [Document: {document_title}, Page: {page_number}, Section: {chunk_type}]
        """
    
    async def answer_legal_question(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        context_limit: int = 5,
        min_similarity: float = 0.7,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a legal question using RAG approach
        
        Args:
            question: The legal question to answer
            document_ids: Optional filter by specific documents
            user_id: User ID for access control
            context_limit: Maximum number of context chunks to use
            min_similarity: Minimum similarity threshold for retrieved content
            include_analysis: Whether to include detailed legal analysis
            
        Returns:
            RAG response with answer, sources, and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Step 1: Retrieve relevant context using semantic search
            search_results = await self.search_service.semantic_search(
                query=question,
                document_ids=document_ids,
                user_id=user_id,
                limit=context_limit * 2,  # Get more results to select best ones
                similarity_threshold=min_similarity,
                include_hybrid=True
            )
            
            if not search_results.get("results"):
                return self._generate_no_context_response(question, "No relevant content found in documents")
            
            # Step 2: Select and prepare context
            context_chunks = self._select_best_context(search_results["results"], context_limit)
            formatted_context = self._format_context_for_llm(context_chunks)
            
            # Step 3: Generate answer using Gemini
            answer_response = await self._generate_answer(question, formatted_context, include_analysis)
            
            # Step 4: Log the interaction for analytics
            await self._log_rag_interaction(
                user_id=user_id,
                question=question,
                context_chunks=len(context_chunks),
                response_generated=bool(answer_response.get("answer"))
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "question": question,
                "answer": answer_response.get("answer", ""),
                "sources": self._extract_sources(context_chunks),
                "legal_analysis": answer_response.get("analysis", {}) if include_analysis else {},
                "context_used": len(context_chunks),
                "confidence_indicators": self._assess_confidence(context_chunks, answer_response),
                "search_metadata": search_results.get("search_metadata", {}),
                "response_metadata": {
                    "response_time": response_time,
                    "model_used": "gemini-1.5-pro",
                    "context_chunks": len(context_chunks),
                    "timestamp": start_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG question answering: {str(e)}")
            return self._generate_error_response(question, str(e))
    
    def _select_best_context(
        self, 
        search_results: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Select the best context chunks for RAG"""
        
        # Sort by similarity score and select top results
        sorted_results = sorted(
            search_results, 
            key=lambda x: x.get('similarity_score', 0), 
            reverse=True
        )
        
        selected_chunks = []
        seen_documents = set()
        total_chars = 0
        max_chars = 4000  # Gemini context limit consideration
        
        for result in sorted_results:
            # Ensure diversity across documents
            doc_id = result.get('document_id', '')
            
            # Add chunk if we haven't exceeded limits
            chunk_chars = len(result.get('content', ''))
            
            if (len(selected_chunks) < limit and 
                total_chars + chunk_chars < max_chars):
                
                selected_chunks.append(result)
                seen_documents.add(doc_id)
                total_chars += chunk_chars
            
            # Stop if we have enough diverse content
            if len(selected_chunks) >= limit:
                break
        
        return selected_chunks
    
    def _format_context_for_llm(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Format context chunks for LLM consumption"""
        
        formatted_context = "LEGAL DOCUMENT CONTEXT:\n\n"
        
        for i, chunk in enumerate(context_chunks, 1):
            doc_title = chunk.get('document_title', 'Unknown Document')
            chunk_type = chunk.get('chunk_type', 'paragraph')
            page_num = chunk.get('page_number', 'Unknown')
            content = chunk.get('content', '')
            similarity = chunk.get('similarity_score', 0)
            
            formatted_context += f"""
[SOURCE {i}]
Document: {doc_title}
Type: {chunk_type.title()}
Page: {page_num}
Similarity: {similarity:.2f}
Content: {content}

---
"""
        
        return formatted_context
    
    async def _generate_answer(
        self, 
        question: str, 
        context: str, 
        include_analysis: bool
    ) -> Dict[str, Any]:
        """Generate answer using Gemini"""
        
        try:
            # Construct the prompt
            if include_analysis:
                analysis_instruction = """
                Additionally, provide a legal analysis section that includes:
                - Key legal concepts identified
                - Potential implications
                - Areas that may need further legal review
                - Relevant legal principles or precedents mentioned
                """
            else:
                analysis_instruction = ""
            
            prompt = f"""
            {self.system_prompt}
            
            {analysis_instruction}
            
            CONTEXT FROM LEGAL DOCUMENTS:
            {context}
            
            QUESTION: {question}
            
            Please provide a comprehensive answer based solely on the provided document context.
            Include specific citations using the format: [Document: title, Page: number, Section: type]
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the response to extract analysis if requested
                full_response = response.text
                
                if include_analysis:
                    # Simple parsing - in production, could use more sophisticated extraction
                    analysis = self._extract_legal_analysis(full_response)
                else:
                    analysis = {}
                
                return {
                    "answer": full_response,
                    "analysis": analysis
                }
            else:
                return {"answer": "Unable to generate response", "analysis": {}}
                
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {"answer": f"Error generating response: {str(e)}", "analysis": {}}
    
    def _extract_legal_analysis(self, response_text: str) -> Dict[str, Any]:
        """Extract structured legal analysis from response"""
        
        # Simple keyword-based extraction
        # In production, would use more sophisticated NLP
        
        analysis = {
            "key_concepts": [],
            "implications": [],
            "review_needed": [],
            "legal_principles": []
        }
        
        response_lower = response_text.lower()
        
        # Extract key legal concepts
        legal_keywords = [
            "contract", "agreement", "obligation", "liability", "breach", 
            "termination", "confidentiality", "payment", "dispute", "rights", 
            "duties", "warranties", "indemnification"
        ]
        
        for keyword in legal_keywords:
            if keyword in response_lower:
                analysis["key_concepts"].append(keyword.title())
        
        # Look for implication indicators
        if any(phrase in response_lower for phrase in ["may result", "could lead", "implies", "suggests"]):
            analysis["implications"].append("Potential consequences identified in response")
        
        # Look for review indicators
        if any(phrase in response_lower for phrase in ["review", "clarification", "ambiguous", "unclear"]):
            analysis["review_needed"].append("Professional legal review recommended")
        
        return analysis
    
    def _extract_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from context chunks"""
        
        sources = []
        for chunk in context_chunks:
            source = {
                "document_id": chunk.get("document_id"),
                "document_title": chunk.get("document_title", "Unknown Document"),
                "document_filename": chunk.get("document_filename", ""),
                "page_number": chunk.get("page_number"),
                "chunk_type": chunk.get("chunk_type"),
                "similarity_score": round(chunk.get("similarity_score", 0), 3),
                "excerpt": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", "")
            }
            sources.append(source)
        
        return sources
    
    def _assess_confidence(
        self, 
        context_chunks: List[Dict[str, Any]], 
        answer_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess confidence indicators for the response"""
        
        if not context_chunks:
            return {"confidence": "low", "reasons": ["No relevant context found"]}
        
        avg_similarity = sum(chunk.get("similarity_score", 0) for chunk in context_chunks) / len(context_chunks)
        
        confidence_indicators = {
            "average_similarity": round(avg_similarity, 3),
            "context_chunks_used": len(context_chunks),
            "document_diversity": len(set(chunk.get("document_id") for chunk in context_chunks)),
            "confidence_level": "high" if avg_similarity > 0.8 else "medium" if avg_similarity > 0.6 else "low"
        }
        
        # Add confidence reasons
        reasons = []
        if avg_similarity > 0.8:
            reasons.append("High similarity scores in retrieved content")
        if len(context_chunks) >= 3:
            reasons.append("Multiple relevant sources found")
        if confidence_indicators["document_diversity"] > 1:
            reasons.append("Content from multiple documents")
            
        confidence_indicators["reasons"] = reasons
        
        return confidence_indicators
    
    async def _log_rag_interaction(
        self,
        user_id: Optional[str],
        question: str,
        context_chunks: int,
        response_generated: bool
    ):
        """Log RAG interaction for analytics"""
        try:
            log_data = {
                "user_id": user_id,
                "query": question,
                "query_type": "rag",
                "results_count": context_chunks,
                "search_time": 0,  # Would be calculated from search service
                "response_generated": response_generated,
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("search_analytics").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging RAG interaction: {str(e)}")
    
    def _generate_no_context_response(self, question: str, reason: str) -> Dict[str, Any]:
        """Generate response when no relevant context is found"""
        return {
            "question": question,
            "answer": f"I cannot find relevant information in the available documents to answer your question about: {question}. {reason}",
            "sources": [],
            "legal_analysis": {},
            "context_used": 0,
            "confidence_indicators": {"confidence": "none", "reasons": [reason]},
            "response_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gemini-1.5-pro",
                "context_chunks": 0
            }
        }
    
    def _generate_error_response(self, question: str, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "question": question,
            "answer": "An error occurred while processing your question. Please try again or contact support.",
            "sources": [],
            "error": error,
            "response_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "error": True
            }
        }
    
    async def generate_document_summary(
        self,
        document_id: str,
        user_id: Optional[str] = None,
        summary_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate a summary of a legal document"""
        
        try:
            # Get all chunks from the document
            from app.services.document_storage import DocumentStorageService
            storage_service = DocumentStorageService()
            
            chunks = await storage_service.get_document_chunks(document_id)
            document_info = await storage_service.get_document_content(document_id)
            
            if not chunks or not document_info:
                return {"error": "Document not found or has no content"}
            
            # Prepare content for summarization
            full_content = "\n\n".join([chunk["content"] for chunk in chunks])
            
            # Generate summary based on type
            if summary_type == "comprehensive":
                summary_prompt = """
                Provide a comprehensive summary of this legal document including:
                1. Document type and purpose
                2. Key parties involved
                3. Main obligations and rights
                4. Important terms and conditions
                5. Key dates and deadlines
                6. Risk factors and considerations
                """
            elif summary_type == "executive":
                summary_prompt = """
                Provide an executive summary focusing on:
                1. Business purpose of the document
                2. Key commercial terms
                3. Major risks and obligations
                4. Critical deadlines
                """
            else:
                summary_prompt = "Provide a concise summary of the main points in this legal document."
            
            prompt = f"""
            {self.system_prompt}
            
            {summary_prompt}
            
            DOCUMENT CONTENT:
            Title: {document_info.get('title', 'Unknown')}
            Type: {document_info.get('document_type', 'Unknown')}
            
            {full_content}
            
            Please provide the requested summary.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "document_id": document_id,
                "document_title": document_info.get('title', 'Unknown'),
                "summary_type": summary_type,
                "summary": response.text if response and response.text else "Unable to generate summary",
                "metadata": {
                    "total_chunks": len(chunks),
                    "document_type": document_info.get('document_type'),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return {"error": str(e)}
