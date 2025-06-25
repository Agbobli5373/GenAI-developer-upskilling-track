"""
Enhanced Legal RAG Service for Week 5
Advanced question answering with legal intelligence, query optimization, and enhanced context processing
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import re
import json

import google.generativeai as genai
from app.core.config import settings
from app.services.search_service import AdvancedLegalSearchService
from app.services.embedding_service import LegalEmbeddingService
from app.core.database import supabase

logger = logging.getLogger(__name__)


class EnhancedLegalRAGService:
    """Enhanced RAG service with advanced legal intelligence and query optimization"""
    
    def __init__(self):
        # Initialize Google Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('Gemini-2.0-Flash')
        self.advanced_search = AdvancedLegalSearchService()
        self.embedding_service = LegalEmbeddingService()
        
        # Enhanced legal domain patterns
        self.legal_question_patterns = {
            'definition': ['what is', 'define', 'meaning of', 'definition of'],
            'procedure': ['how to', 'process for', 'steps to', 'procedure'],
            'obligation': ['must', 'required to', 'obligated to', 'responsible for'],
            'rights': ['can', 'allowed to', 'entitled to', 'rights to'],
            'consequence': ['what happens if', 'penalty for', 'result of', 'consequence'],
            'timeline': ['when', 'deadline', 'period', 'duration'],
            'exception': ['except', 'unless', 'excluding', 'exemption'],
            'comparison': ['difference between', 'compare', 'versus', 'vs']
        }
        
        # Enhanced prompts for different legal question types
        self.specialized_prompts = {
            'definition': """
            Provide a precise legal definition based on the document context.
            Include any specific definitions given in the document and explain their scope.
            """,
            'procedure': """
            Outline the step-by-step process as described in the documents.
            Include any prerequisites, timelines, and potential variations.
            """,
            'obligation': """
            Clearly identify who has the obligation, what the obligation entails,
            and any conditions or exceptions that apply.
            """,
            'rights': """
            Identify the specific rights, who holds them, and any limitations
            or conditions that apply to these rights.
            """,
            'consequence': """
            Explain the specific consequences, penalties, or outcomes described
            in the documents, including any procedural requirements.
            """,
            'timeline': """
            Provide specific dates, deadlines, and time periods mentioned in the documents.
            Include any calculation methods or triggering events.
            """,
            'exception': """
            Identify all exceptions, exclusions, or special conditions mentioned
            in the documents and explain their scope and application.
            """,
            'comparison': """
            Provide a detailed comparison highlighting similarities, differences,
            and unique aspects of each item being compared.
            """
        }
        
        # Enhanced system prompt
        self.enhanced_system_prompt = """
        You are an advanced legal document analysis AI with deep understanding of legal concepts,
        terminology, and document structures. You specialize in providing precise, well-sourced
        analysis of legal documents for legal professionals.

        CORE CAPABILITIES:
        1. Legal document interpretation and analysis
        2. Clause identification and cross-referencing
        3. Legal concept explanation and definition
        4. Compliance and obligation analysis
        5. Risk identification and assessment

        ANALYSIS FRAMEWORK:
        1. DIRECT ANSWER: Provide clear, direct response to the question
        2. LEGAL CONTEXT: Explain relevant legal concepts and terminology
        3. DOCUMENT CITATIONS: Reference specific sections, clauses, and page numbers
        4. CROSS-REFERENCES: Identify related provisions in the same or other documents
        5. IMPLICATIONS: Highlight potential legal implications and considerations
        6. RECOMMENDATIONS: Suggest areas requiring further legal review

        RESPONSE STRUCTURE:
        **Direct Answer**: [Clear, concise answer to the question]
        
        **Legal Analysis**: [Detailed analysis with legal context]
        
        **Document References**: [Specific citations with locations]
        
        **Related Provisions**: [Cross-references to related clauses]
        
        **Legal Implications**: [Potential implications and considerations]
        
        **Professional Review**: [Areas needing attorney review]

        QUALITY STANDARDS:
        - Use precise legal terminology
        - Maintain professional, authoritative tone
        - Provide complete source attribution
        - Identify ambiguities or unclear provisions
        - Never provide legal advice - only document analysis
        - Include appropriate disclaimers
        """
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the legal question to determine optimal processing strategy"""
        question_lower = question.lower()
        
        # Score each question type
        type_scores = {}
        for q_type, patterns in self.legal_question_patterns.items():
            score = sum(1 for pattern in patterns if pattern in question_lower)
            if score > 0:
                type_scores[q_type] = score
        
        # Return highest scoring type or 'general' if no match
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return 'general'
    
    def _extract_legal_entities_from_question(self, question: str) -> Dict[str, List[str]]:
        """Extract legal entities and concepts from the question"""
        entities = {
            'parties': [],
            'document_types': [],
            'legal_concepts': [],
            'actions': [],
            'time_references': []
        }
        
        question_lower = question.lower()
        
        # Party patterns
        party_patterns = ['party', 'parties', 'plaintiff', 'defendant', 'client', 'customer', 'vendor', 'contractor']
        entities['parties'] = [p for p in party_patterns if p in question_lower]
        
        # Document type patterns
        doc_patterns = ['contract', 'agreement', 'policy', 'clause', 'provision', 'amendment', 'addendum']
        entities['document_types'] = [d for d in doc_patterns if d in question_lower]
        
        # Legal concept patterns
        legal_patterns = ['liability', 'obligation', 'rights', 'termination', 'breach', 'confidentiality', 'intellectual property']
        entities['legal_concepts'] = [l for l in legal_patterns if l in question_lower]
        
        # Action patterns
        action_patterns = ['terminate', 'breach', 'modify', 'assign', 'transfer', 'renew', 'cancel']
        entities['actions'] = [a for a in action_patterns if a in question_lower]
        
        # Time reference patterns
        time_patterns = ['deadline', 'period', 'term', 'expiration', 'renewal', 'notice period']
        entities['time_references'] = [t for t in time_patterns if t in question_lower]
        
        return entities
    
    def _optimize_search_query(self, question: str, question_type: str, entities: Dict[str, List[str]]) -> str:
        """Optimize the search query based on question analysis"""
        # Start with the original question
        optimized_query = question
        
        # Add legal context based on question type
        if question_type == 'definition':
            optimized_query += " definition meaning terminology"
        elif question_type == 'procedure':
            optimized_query += " process steps procedure requirements"
        elif question_type == 'obligation':
            optimized_query += " obligation duty responsibility requirements"
        elif question_type == 'rights':
            optimized_query += " rights entitlement authority permission"
        elif question_type == 'consequence':
            optimized_query += " consequence penalty result outcome"
        elif question_type == 'timeline':
            optimized_query += " deadline period time duration"
        
        # Add extracted entities
        for entity_type, entity_list in entities.items():
            if entity_list:
                optimized_query += " " + " ".join(entity_list)
        
        return optimized_query
    
    async def enhanced_question_answering(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        context_limit: int = 8,
        min_similarity: float = 0.7,
        include_analysis: bool = True,
        enable_cross_reference: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced question answering with legal intelligence and optimization
        
        Args:
            question: Legal question to answer
            document_ids: Optional filter by document IDs
            user_id: User ID for access control
            context_limit: Maximum number of context chunks
            min_similarity: Minimum similarity threshold
            include_analysis: Whether to include detailed legal analysis
            enable_cross_reference: Whether to find cross-references
            
        Returns:
            Enhanced answer with legal analysis and citations
        """
        try:
            start_time = datetime.utcnow()
            
            # Step 1: Analyze the question
            question_type = self._classify_question_type(question)
            entities = self._extract_legal_entities_from_question(question)
            
            logger.info(f"Question analysis - Type: {question_type}, Entities: {entities}")
            
            # Step 2: Optimize search query
            optimized_query = self._optimize_search_query(question, question_type, entities)
            
            # Step 3: Perform enhanced search for context
            search_results = await self.advanced_search.advanced_semantic_search(
                query=optimized_query,
                document_ids=document_ids,
                user_id=user_id,
                limit=context_limit,
                similarity_threshold=min_similarity,
                enable_caching=True,
                include_suggestions=False
            )
            
            if not search_results.get('results'):
                return self._empty_answer_result(question, "No relevant content found")
            
            # Step 4: Prepare enhanced context
            context_chunks = search_results['results']
            enhanced_context = self._prepare_enhanced_context(context_chunks, question_type)
            
            # Step 5: Find cross-references if enabled
            cross_references = []
            if enable_cross_reference and len(context_chunks) > 0:
                cross_references = await self._find_cross_references(
                    context_chunks, 
                    question, 
                    document_ids, 
                    user_id
                )
            
            # Step 6: Generate specialized prompt
            specialized_prompt = self._generate_specialized_prompt(question, question_type)
            
            # Step 7: Generate enhanced answer
            answer_response = await self._generate_enhanced_answer(
                question=question,
                context=enhanced_context,
                specialized_prompt=specialized_prompt,
                question_type=question_type,
                cross_references=cross_references
            )
            
            # Step 8: Perform legal analysis if requested
            legal_analysis = {}
            if include_analysis:
                legal_analysis = await self._perform_legal_analysis(
                    question=question,
                    answer=answer_response,
                    context_chunks=context_chunks,
                    question_type=question_type,
                    entities=entities
                )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            # Step 9: Compile enhanced response
            enhanced_response = {
                'question': question,
                'answer': answer_response,
                'question_analysis': {
                    'type': question_type,
                    'entities': entities,
                    'optimized_query': optimized_query
                },
                'context_used': len(context_chunks),
                'sources': self._format_enhanced_sources(context_chunks),
                'cross_references': cross_references,
                'legal_analysis': legal_analysis,
                'confidence_score': self._calculate_confidence_score(
                    context_chunks, question, answer_response
                ),
                'response_time': response_time,
                'recommendations': self._generate_recommendations(
                    question_type, legal_analysis, context_chunks
                )
            }
            
            # Step 10: Log analytics
            await self._log_rag_analytics(
                user_id=user_id,
                question=question,
                question_type=question_type,
                context_used=len(context_chunks),
                response_time=response_time,
                confidence_score=enhanced_response['confidence_score']
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error in enhanced question answering: {str(e)}")
            return self._empty_answer_result(question, str(e))
    
    def _prepare_enhanced_context(self, context_chunks: List[Dict[str, Any]], question_type: str) -> str:
        """Prepare enhanced context with legal structuring"""
        
        # Group chunks by document for better organization
        docs_context = {}
        for chunk in context_chunks:
            doc_id = chunk.get('document_id', 'unknown')
            doc_title = chunk.get('document_title', 'Unknown Document')
            
            if doc_id not in docs_context:
                docs_context[doc_id] = {
                    'title': doc_title,
                    'chunks': []
                }
            
            docs_context[doc_id]['chunks'].append(chunk)
        
        # Build enhanced context string
        context_parts = []
        
        for doc_id, doc_data in docs_context.items():
            context_parts.append(f"\n=== DOCUMENT: {doc_data['title']} ===")
            
            for i, chunk in enumerate(doc_data['chunks'], 1):
                chunk_info = f"\n[Section {i}]"
                if chunk.get('page_number'):
                    chunk_info += f" (Page {chunk['page_number']})"
                if chunk.get('chunk_type'):
                    chunk_info += f" [{chunk['chunk_type']}]"
                
                context_parts.append(chunk_info)
                context_parts.append(chunk.get('content', ''))
        
        return "\n".join(context_parts)
    
    def _generate_specialized_prompt(self, question: str, question_type: str) -> str:
        """Generate specialized prompt based on question type"""
        base_prompt = self.enhanced_system_prompt
        
        if question_type in self.specialized_prompts:
            specialized_instruction = self.specialized_prompts[question_type]
            base_prompt += f"\n\nSPECIAL INSTRUCTIONS FOR {question_type.upper()} QUESTIONS:\n{specialized_instruction}"
        
        return base_prompt
    
    async def _generate_enhanced_answer(
        self,
        question: str,
        context: str,
        specialized_prompt: str,
        question_type: str,
        cross_references: List[Dict[str, Any]]
    ) -> str:
        """Generate enhanced answer using specialized prompts"""
        
        # Build the prompt
        prompt = f"{specialized_prompt}\n\n"
        prompt += f"QUESTION TYPE: {question_type}\n\n"
        prompt += f"LEGAL QUESTION: {question}\n\n"
        prompt += f"DOCUMENT CONTEXT:\n{context}\n\n"
        
        if cross_references:
            prompt += "CROSS-REFERENCES:\n"
            for ref in cross_references:
                prompt += f"- {ref.get('description', 'Related provision')}\n"
            prompt += "\n"
        
        prompt += "Provide a comprehensive legal analysis following the response structure outlined above."
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text if response.text else "Unable to generate response"
            
        except Exception as e:
            logger.error(f"Error generating enhanced answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    async def _find_cross_references(
        self,
        context_chunks: List[Dict[str, Any]],
        question: str,
        document_ids: Optional[List[str]],
        user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Find cross-references and related provisions"""
        
        cross_references = []
        
        try:
            # Extract key terms from context chunks
            key_terms = set()
            for chunk in context_chunks:
                content = chunk.get('content', '').lower()
                # Extract legal terms (simple approach)
                legal_terms = re.findall(r'\b(?:shall|must|may|will|agreement|contract|party|clause|provision)\b', content)
                key_terms.update(legal_terms)
            
            # Search for related content using key terms
            if key_terms:
                cross_ref_query = " ".join(list(key_terms)[:5])  # Use top 5 terms
                
                related_results = await self.advanced_search.semantic_search(
                    query=cross_ref_query,
                    document_ids=document_ids,
                    user_id=user_id,
                    limit=5,
                    similarity_threshold=0.6
                )
                
                # Filter out chunks already in main context
                existing_chunk_ids = {chunk.get('id') for chunk in context_chunks}
                
                for result in related_results.get('results', []):
                    if result.get('id') not in existing_chunk_ids:
                        cross_references.append({
                            'document_title': result.get('document_title', 'Unknown'),
                            'content_preview': result.get('content', '')[:200] + "...",
                            'similarity_score': result.get('similarity_score', 0),
                            'page_number': result.get('page_number'),
                            'description': 'Related provision'
                        })
                
                # Limit cross-references
                cross_references = cross_references[:3]
                
        except Exception as e:
            logger.error(f"Error finding cross-references: {str(e)}")
        
        return cross_references
    
    async def _perform_legal_analysis(
        self,
        question: str,
        answer: str,
        context_chunks: List[Dict[str, Any]],
        question_type: str,
        entities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Perform detailed legal analysis of the answer and context"""
        
        analysis = {
            'document_coverage': {},
            'legal_concepts_identified': [],
            'potential_risks': [],
            'compliance_considerations': [],
            'ambiguities_found': [],
            'recommendation_confidence': 'medium'
        }
        
        try:
            # Document coverage analysis
            doc_distribution = {}
            for chunk in context_chunks:
                doc_title = chunk.get('document_title', 'Unknown')
                doc_distribution[doc_title] = doc_distribution.get(doc_title, 0) + 1
            
            analysis['document_coverage'] = doc_distribution
            
            # Legal concept identification
            legal_concepts = set()
            for chunk in context_chunks:
                content = chunk.get('content', '').lower()
                
                # Extract legal concepts (expanded patterns)
                concepts = re.findall(
                    r'\b(?:liability|obligation|breach|termination|confidentiality|indemnification|'
                    r'warranty|representation|covenant|condition|precedent|subsequent|'
                    r'force majeure|intellectual property|trade secret|copyright|patent)\b',
                    content
                )
                legal_concepts.update(concepts)
            
            analysis['legal_concepts_identified'] = list(legal_concepts)
            
            # Risk identification (basic patterns)
            risk_patterns = [
                'penalty', 'fine', 'damages', 'breach', 'default', 'termination',
                'liability', 'indemnification', 'unlimited', 'consequential'
            ]
            
            risks_found = []
            for chunk in context_chunks:
                content = chunk.get('content', '').lower()
                for pattern in risk_patterns:
                    if pattern in content:
                        risks_found.append(f"Potential {pattern} exposure found")
            
            analysis['potential_risks'] = list(set(risks_found))[:5]  # Top 5 unique risks
            
            # Compliance considerations
            compliance_terms = ['compliance', 'regulation', 'law', 'statute', 'rule', 'requirement']
            compliance_found = []
            
            for chunk in context_chunks:
                content = chunk.get('content', '').lower()
                for term in compliance_terms:
                    if term in content:
                        compliance_found.append(f"Compliance with {term} mentioned")
            
            analysis['compliance_considerations'] = list(set(compliance_found))[:3]
            
            # Ambiguity detection (simple heuristics)
            ambiguity_indicators = ['may', 'might', 'could', 'should', 'reasonable', 'appropriate', 'as needed']
            ambiguities = []
            
            for chunk in context_chunks:
                content = chunk.get('content', '').lower()
                for indicator in ambiguity_indicators:
                    if indicator in content:
                        ambiguities.append(f"Ambiguous language: '{indicator}' found")
            
            analysis['ambiguities_found'] = list(set(ambiguities))[:3]
            
            # Confidence scoring
            if len(context_chunks) >= 3 and len(legal_concepts) >= 2:
                analysis['recommendation_confidence'] = 'high'
            elif len(context_chunks) >= 2 or len(legal_concepts) >= 1:
                analysis['recommendation_confidence'] = 'medium'
            else:
                analysis['recommendation_confidence'] = 'low'
                
        except Exception as e:
            logger.error(f"Error in legal analysis: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _calculate_confidence_score(
        self,
        context_chunks: List[Dict[str, Any]],
        question: str,
        answer: str
    ) -> float:
        """Calculate confidence score for the answer"""
        
        score = 0.5  # Base score
        
        # Factor 1: Number of high-quality context chunks
        high_quality_chunks = [c for c in context_chunks if c.get('similarity_score', 0) > 0.8]
        score += min(len(high_quality_chunks) * 0.1, 0.3)
        
        # Factor 2: Answer length and completeness
        if len(answer) > 200:
            score += 0.1
        if 'document' in answer.lower() and 'section' in answer.lower():
            score += 0.1
        
        # Factor 3: Multiple document sources
        unique_docs = len(set(c.get('document_id') for c in context_chunks))
        if unique_docs > 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendations(
        self,
        question_type: str,
        legal_analysis: Dict[str, Any],
        context_chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        
        recommendations = []
        
        # Question type specific recommendations
        if question_type == 'obligation':
            recommendations.append("Review all related obligations and their interconnections")
        elif question_type == 'timeline':
            recommendations.append("Verify all dates and deadlines for accuracy and feasibility")
        elif question_type == 'consequence':
            recommendations.append("Consider the full impact and potential mitigation strategies")
        
        # Risk-based recommendations
        if legal_analysis.get('potential_risks'):
            recommendations.append("Conduct thorough risk assessment for identified exposures")
        
        # Compliance recommendations
        if legal_analysis.get('compliance_considerations'):
            recommendations.append("Verify compliance with all applicable regulations")
        
        # Ambiguity recommendations
        if legal_analysis.get('ambiguities_found'):
            recommendations.append("Clarify ambiguous language with legal counsel")
        
        # Coverage recommendations
        if len(context_chunks) < 3:
            recommendations.append("Consider reviewing additional related documents")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Have this analysis reviewed by qualified legal counsel")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _format_enhanced_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources with enhanced information"""
        
        formatted_sources = []
        
        for chunk in context_chunks:
            source = {
                'document_title': chunk.get('document_title', 'Unknown Document'),
                'document_id': chunk.get('document_id'),
                'page_number': chunk.get('page_number'),
                'chunk_type': chunk.get('chunk_type'),
                'similarity_score': chunk.get('similarity_score', 0),
                'content_preview': chunk.get('content', '')[:150] + "...",
                'location': {
                    'paragraph_index': chunk.get('paragraph_index'),
                    'char_start': chunk.get('char_start'),
                    'char_end': chunk.get('char_end')
                }
            }
            formatted_sources.append(source)
        
        return formatted_sources
    
    async def _log_rag_analytics(
        self,
        user_id: Optional[str],
        question: str,
        question_type: str,
        context_used: int,
        response_time: float,
        confidence_score: float
    ) -> None:
        """Log RAG analytics for performance tracking"""
        
        try:
            analytics_data = {
                'user_id': user_id,
                'question': question,
                'question_type': question_type,
                'context_chunks_used': context_used,
                'response_time': response_time,
                'confidence_score': confidence_score,
                'service_type': 'enhanced_rag',
                'created_at': datetime.utcnow().isoformat()
            }
            
            supabase.table("rag_analytics").insert(analytics_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging RAG analytics: {str(e)}")
    
    def _empty_answer_result(self, question: str, error_message: str) -> Dict[str, Any]:
        """Return empty answer result with error information"""
        
        return {
            'question': question,
            'answer': f"Unable to answer the question: {error_message}",
            'question_analysis': {
                'type': 'unknown',
                'entities': {},
                'optimized_query': question
            },
            'context_used': 0,
            'sources': [],
            'cross_references': [],
            'legal_analysis': {},
            'confidence_score': 0.0,
            'response_time': 0,
            'recommendations': ['Please try rephrasing your question or check document availability'],
            'error': error_message
        }
    
    async def batch_question_processing(
        self,
        questions: List[str],
        document_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Process multiple questions concurrently with rate limiting"""
        
        async def process_single_question(question: str) -> Dict[str, Any]:
            return await self.enhanced_question_answering(
                question=question,
                document_ids=document_ids,
                user_id=user_id
            )
        
        # Process questions in batches to avoid overwhelming the system
        results = []
        
        for i in range(0, len(questions), max_concurrent):
            batch = questions[i:i + max_concurrent]
            batch_tasks = [process_single_question(q) for q in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append(self._empty_answer_result(
                        batch[j], 
                        f"Batch processing error: {str(result)}"
                    ))
                else:
                    results.append(result)
        
        return results
    
    async def get_rag_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get RAG service analytics and performance metrics"""
        
        try:
            # Build query
            query = supabase.table("rag_analytics").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.limit(100).order("created_at", desc=True).execute()
            
            if not result.data:
                return {
                    'total_questions': 0,
                    'avg_response_time': 0,
                    'avg_confidence_score': 0,
                    'question_types': {},
                    'recent_activity': []
                }
            
            # Calculate analytics
            data = result.data
            total_questions = len(data)
            avg_response_time = sum(item.get('response_time', 0) for item in data) / total_questions
            avg_confidence = sum(item.get('confidence_score', 0) for item in data) / total_questions
            
            # Question type distribution
            question_types = {}
            for item in data:
                q_type = item.get('question_type', 'unknown')
                question_types[q_type] = question_types.get(q_type, 0) + 1
            
            return {
                'total_questions': total_questions,
                'avg_response_time': round(avg_response_time, 3),
                'avg_confidence_score': round(avg_confidence, 3),
                'question_types': question_types,
                'recent_activity': data[:10]  # Last 10 questions
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG analytics: {str(e)}")
            return {'error': str(e)}
