"""
Query Optimization Service for Week 5
Advanced query processing, optimization, and intent understanding
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import re
import json
from collections import Counter

import google.generativeai as genai
from app.core.config import settings
from app.core.database import supabase

logger = logging.getLogger(__name__)


class QueryOptimizationService:
    """Advanced query optimization and processing service"""
    
    def __init__(self):
        # Initialize Google Gemini for query understanding
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('Gemini-2.0-Flash')
        
        # Legal query patterns and synonyms
        self.legal_synonyms = {
            'contract': ['agreement', 'compact', 'accord', 'deal', 'pact'],
            'clause': ['provision', 'section', 'article', 'paragraph', 'term'],
            'obligation': ['duty', 'responsibility', 'requirement', 'commitment'],
            'termination': ['cancellation', 'ending', 'dissolution', 'expiration'],
            'liability': ['responsibility', 'accountability', 'fault', 'blame'],
            'breach': ['violation', 'default', 'failure', 'non-compliance'],
            'amendment': ['modification', 'change', 'revision', 'alteration'],
            'confidentiality': ['secrecy', 'non-disclosure', 'privacy', 'discretion'],
            'intellectual property': ['IP', 'patent', 'copyright', 'trademark', 'trade secret'],
            'indemnification': ['compensation', 'reimbursement', 'protection', 'coverage'],
            'force majeure': ['act of god', 'unforeseeable circumstances', 'extraordinary events'],
            'warranty': ['guarantee', 'assurance', 'promise', 'representation']
        }
        
        # Query expansion patterns
        self.expansion_patterns = {
            'definition_query': {
                'triggers': ['what is', 'define', 'meaning of', 'definition'],
                'expansions': ['definition', 'meaning', 'interpretation', 'explanation']
            },
            'procedure_query': {
                'triggers': ['how to', 'process for', 'steps to', 'procedure'],
                'expansions': ['process', 'procedure', 'steps', 'method', 'approach']
            },
            'timeline_query': {
                'triggers': ['when', 'deadline', 'period', 'time'],
                'expansions': ['deadline', 'period', 'duration', 'timeframe', 'schedule']
            },
            'consequence_query': {
                'triggers': ['what happens', 'result', 'consequence', 'penalty'],
                'expansions': ['consequence', 'result', 'outcome', 'penalty', 'effect']
            },
            'comparison_query': {
                'triggers': ['difference', 'compare', 'versus', 'vs'],
                'expansions': ['comparison', 'difference', 'distinction', 'contrast']
            }
        }
        
        # Query complexity indicators
        self.complexity_indicators = {
            'simple': ['what', 'when', 'who', 'where'],
            'moderate': ['how', 'why', 'which', 'difference'],
            'complex': ['analyze', 'compare', 'evaluate', 'determine', 'assess'],
            'advanced': ['implications', 'consequences', 'relationships', 'dependencies']
        }
        
        # Cache for query optimizations
        self._optimization_cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    def _extract_query_intent(self, query: str) -> Dict[str, Any]:
        """Extract intent and structure from the query"""
        
        query_lower = query.lower().strip()
        
        intent_analysis = {
            'primary_intent': 'general',
            'secondary_intents': [],
            'entities': [],
            'legal_concepts': [],
            'query_type': 'factual',
            'complexity': 'simple',
            'requires_analysis': False,
            'multi_document': False
        }
        
        # Determine primary intent
        for intent_type, patterns in self.expansion_patterns.items():
            for trigger in patterns['triggers']:
                if trigger in query_lower:
                    intent_analysis['primary_intent'] = intent_type.replace('_query', '')
                    break
        
        # Detect complexity level
        for complexity, indicators in self.complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                intent_analysis['complexity'] = complexity
                break
        
        # Extract legal concepts
        legal_concepts = []
        for concept, synonyms in self.legal_synonyms.items():
            if concept in query_lower or any(syn in query_lower for syn in synonyms):
                legal_concepts.append(concept)
        
        intent_analysis['legal_concepts'] = legal_concepts
        
        # Detect if analysis is required
        analysis_indicators = ['analyze', 'evaluate', 'assess', 'implications', 'impact', 'risk']
        intent_analysis['requires_analysis'] = any(indicator in query_lower for indicator in analysis_indicators)
        
        # Detect multi-document queries
        multi_doc_indicators = ['compare', 'contrast', 'difference', 'similar', 'across documents']
        intent_analysis['multi_document'] = any(indicator in query_lower for indicator in multi_doc_indicators)
        
        # Extract entities (simple pattern matching)
        entities = []
        
        # Party entities
        party_patterns = re.findall(r'\b(?:party|parties|client|vendor|contractor|employer|employee)\b', query_lower)
        entities.extend(party_patterns)
        
        # Document entities
        doc_patterns = re.findall(r'\b(?:contract|agreement|policy|clause|section|article)\b', query_lower)
        entities.extend(doc_patterns)
        
        intent_analysis['entities'] = list(set(entities))
        
        return intent_analysis
    
    def _expand_query_terms(self, query: str, intent: Dict[str, Any]) -> str:
        """Expand query with legal synonyms and related terms"""
        
        expanded_terms = set()
        query_words = query.lower().split()
        
        # Add synonyms for legal concepts
        for concept in intent['legal_concepts']:
            if concept in self.legal_synonyms:
                expanded_terms.update(self.legal_synonyms[concept][:3])  # Top 3 synonyms
        
        # Add intent-specific expansions
        primary_intent = intent['primary_intent']
        if primary_intent in [pattern.replace('_query', '') for pattern in self.expansion_patterns]:
            pattern_key = f"{primary_intent}_query"
            if pattern_key in self.expansion_patterns:
                expanded_terms.update(self.expansion_patterns[pattern_key]['expansions'][:2])
        
        # Combine original query with expansions
        if expanded_terms:
            expansion_text = " ".join(expanded_terms)
            return f"{query} {expansion_text}"
        
        return query
    
    def _optimize_for_legal_context(self, query: str, intent: Dict[str, Any]) -> str:
        """Optimize query specifically for legal document context"""
        
        # Add legal context keywords
        legal_context = "legal document"
        
        # Add specific legal qualifiers based on intent
        if intent['primary_intent'] == 'definition':
            legal_context += " definition terminology"
        elif intent['primary_intent'] == 'procedure':
            legal_context += " process requirements"
        elif intent['primary_intent'] == 'timeline':
            legal_context += " deadline period"
        elif intent['primary_intent'] == 'consequence':
            legal_context += " penalty liability"
        
        # Add complexity-specific terms
        if intent['complexity'] in ['complex', 'advanced']:
            legal_context += " analysis implications"
        
        return f"{query} {legal_context}"
    
    def _generate_alternative_queries(self, original_query: str, intent: Dict[str, Any]) -> List[str]:
        """Generate alternative query formulations"""
        
        alternatives = []
        
        # Rephrase based on intent
        if intent['primary_intent'] == 'definition':
            alternatives.extend([
                f"define {' '.join(intent['legal_concepts'])}",
                f"meaning of {' '.join(intent['legal_concepts'])}",
                f"what does {' '.join(intent['legal_concepts'])} mean"
            ])
        
        elif intent['primary_intent'] == 'procedure':
            alternatives.extend([
                f"how to {original_query.replace('how to', '').strip()}",
                f"process for {original_query.replace('process', '').strip()}",
                f"steps to {original_query.replace('steps', '').strip()}"
            ])
        
        elif intent['primary_intent'] == 'timeline':
            alternatives.extend([
                f"deadline for {original_query.replace('when', '').strip()}",
                f"time period {original_query}",
                f"duration of {original_query}"
            ])
        
        # Add concept-based alternatives
        for concept in intent['legal_concepts']:
            if concept in self.legal_synonyms:
                for synonym in self.legal_synonyms[concept][:2]:
                    alt_query = original_query.replace(concept, synonym)
                    if alt_query != original_query:
                        alternatives.append(alt_query)
        
        # Remove duplicates and limit
        alternatives = list(set(alternatives))[:5]
        
        return alternatives
    
    async def optimize_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        enable_ai_rewriting: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize a query for better legal document search results
        
        Args:
            query: Original query string
            context: Optional context (user preferences, document types, etc.)
            enable_ai_rewriting: Whether to use AI for query rewriting
            
        Returns:
            Optimization result with enhanced queries and metadata
        """
        
        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = f"{query}_{hash(str(context))}"
            if cache_key in self._optimization_cache:
                cached_result = self._optimization_cache[cache_key]
                if (datetime.utcnow() - cached_result['timestamp']).seconds < self._cache_ttl:
                    return cached_result['result']
            
            # Step 1: Extract intent and analyze query
            intent_analysis = self._extract_query_intent(query)
            
            # Step 2: Expand query terms
            expanded_query = self._expand_query_terms(query, intent_analysis)
            
            # Step 3: Optimize for legal context
            legal_optimized_query = self._optimize_for_legal_context(expanded_query, intent_analysis)
            
            # Step 4: Generate alternative queries
            alternative_queries = self._generate_alternative_queries(query, intent_analysis)
            
            # Step 5: AI-powered query rewriting (if enabled)
            ai_rewritten_query = None
            if enable_ai_rewriting and intent_analysis['complexity'] in ['complex', 'advanced']:
                ai_rewritten_query = await self._ai_rewrite_query(query, intent_analysis)
            
            # Step 6: Generate search strategy recommendations
            search_strategy = self._generate_search_strategy(intent_analysis)
            
            optimization_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                'original_query': query,
                'optimized_query': legal_optimized_query,
                'expanded_query': expanded_query,
                'alternative_queries': alternative_queries,
                'ai_rewritten_query': ai_rewritten_query,
                'intent_analysis': intent_analysis,
                'search_strategy': search_strategy,
                'optimization_time': optimization_time,
                'recommendations': self._generate_optimization_recommendations(intent_analysis)
            }
            
            # Cache the result
            self._optimization_cache[cache_key] = {
                'result': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing query: {str(e)}")
            return {
                'original_query': query,
                'optimized_query': query,
                'error': str(e)
            }
    
    async def _ai_rewrite_query(self, query: str, intent: Dict[str, Any]) -> str:
        """Use AI to rewrite complex queries for better legal search"""
        
        rewrite_prompt = f"""
        You are a legal search expert. Rewrite the following query to be more effective for searching legal documents.
        
        Original Query: {query}
        Query Intent: {intent['primary_intent']}
        Legal Concepts: {', '.join(intent['legal_concepts'])}
        Complexity: {intent['complexity']}
        
        Guidelines:
        1. Use precise legal terminology
        2. Include relevant synonyms and related terms
        3. Structure for semantic search effectiveness
        4. Maintain the original intent
        5. Optimize for legal document corpus
        
        Rewritten Query:
        """
        
        try:
            response = await self.model.generate_content_async(rewrite_prompt)
            rewritten = response.text.strip() if response.text else query
            
            # Clean up the response
            if rewritten.startswith('Rewritten Query:'):
                rewritten = rewritten.replace('Rewritten Query:', '').strip()
            
            return rewritten
            
        except Exception as e:
            logger.error(f"Error in AI query rewriting: {str(e)}")
            return query
    
    def _generate_search_strategy(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate search strategy recommendations based on intent"""
        
        strategy = {
            'search_type': 'semantic',
            'similarity_threshold': 0.7,
            'context_window': 5,
            'enable_hybrid': True,
            'chunk_types': [],
            'document_filters': [],
            'post_processing': []
        }
        
        # Adjust strategy based on intent
        if intent['primary_intent'] == 'definition':
            strategy['chunk_types'] = ['definition', 'heading']
            strategy['similarity_threshold'] = 0.8
            strategy['search_type'] = 'hybrid'
        
        elif intent['primary_intent'] == 'procedure':
            strategy['chunk_types'] = ['paragraph', 'list_item']
            strategy['context_window'] = 7
            strategy['post_processing'].append('sequence_ordering')
        
        elif intent['primary_intent'] == 'timeline':
            strategy['chunk_types'] = ['clause', 'paragraph']
            strategy['post_processing'].append('date_extraction')
        
        elif intent['primary_intent'] == 'consequence':
            strategy['chunk_types'] = ['clause', 'paragraph']
            strategy['post_processing'].append('risk_analysis')
        
        # Adjust for complexity
        if intent['complexity'] in ['complex', 'advanced']:
            strategy['context_window'] = 10
            strategy['enable_hybrid'] = True
            strategy['post_processing'].append('cross_reference_analysis')
        
        # Multi-document adjustments
        if intent['multi_document']:
            strategy['post_processing'].append('document_comparison')
            strategy['context_window'] = 3  # Reduce per-document context
        
        return strategy
    
    def _generate_optimization_recommendations(self, intent: Dict[str, Any]) -> List[str]:
        """Generate recommendations for query optimization"""
        
        recommendations = []
        
        # Intent-specific recommendations
        if intent['primary_intent'] == 'general':
            recommendations.append("Consider being more specific about what you're looking for")
        
        if not intent['legal_concepts']:
            recommendations.append("Include specific legal terms for better results")
        
        if intent['complexity'] == 'simple' and intent['requires_analysis']:
            recommendations.append("Your query suggests you need analysis - consider using advanced search")
        
        if intent['multi_document']:
            recommendations.append("Use document comparison feature for multi-document analysis")
        
        # Entity-specific recommendations
        if not intent['entities']:
            recommendations.append("Specify parties, document types, or sections for targeted search")
        
        # Complexity recommendations
        if intent['complexity'] in ['complex', 'advanced']:
            recommendations.append("Consider breaking down complex queries into simpler parts")
            recommendations.append("Use the enhanced RAG service for detailed analysis")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def batch_optimize_queries(
        self,
        queries: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Optimize multiple queries in batch"""
        
        tasks = [self.optimize_query(query, context) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'original_query': queries[i],
                    'optimized_query': queries[i],
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_query_suggestions(
        self,
        partial_query: str,
        document_context: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[str]:
        """Generate intelligent query suggestions based on partial input"""
        
        suggestions = []
        partial_lower = partial_query.lower()
        
        try:
            # Intent-based suggestions
            intent = self._extract_query_intent(partial_query)
            
            # Add common legal question patterns
            if intent['primary_intent'] == 'definition':
                suggestions.extend([
                    f"What is {partial_query}?",
                    f"Define {partial_query}",
                    f"Meaning of {partial_query}"
                ])
            
            elif 'how' in partial_lower:
                suggestions.extend([
                    f"How to {partial_query.replace('how', '').strip()}?",
                    f"Process for {partial_query}",
                    f"Steps to {partial_query}"
                ])
            
            elif 'when' in partial_lower:
                suggestions.extend([
                    f"When does {partial_query.replace('when', '').strip()}?",
                    f"Deadline for {partial_query}",
                    f"Timeline of {partial_query}"
                ])
            
            # Add legal concept specific suggestions
            for concept in intent['legal_concepts']:
                if concept in self.legal_synonyms:
                    for synonym in self.legal_synonyms[concept][:2]:
                        suggestion = partial_query.replace(concept, synonym)
                        if suggestion not in suggestions:
                            suggestions.append(suggestion)
            
            # Add common legal queries
            common_legal_queries = [
                f"What are the {partial_query} requirements?",
                f"What happens if {partial_query}?",
                f"Who is responsible for {partial_query}?",
                f"What are the consequences of {partial_query}?",
                f"How is {partial_query} defined in the contract?"
            ]
            
            suggestions.extend(common_legal_queries)
            
            # Remove duplicates and limit
            suggestions = list(set(suggestions))[:limit]
            
        except Exception as e:
            logger.error(f"Error generating query suggestions: {str(e)}")
        
        return suggestions
    
    async def analyze_query_performance(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze query performance and suggest improvements"""
        
        analysis = {
            'query': query,
            'performance_score': 0.5,
            'result_quality': 'medium',
            'suggestions': [],
            'optimization_opportunities': []
        }
        
        try:
            # Analyze result quality
            if not search_results:
                analysis['performance_score'] = 0.1
                analysis['result_quality'] = 'poor'
                analysis['suggestions'].append("No results found - try broader terms")
            
            elif len(search_results) < 3:
                analysis['performance_score'] = 0.4
                analysis['result_quality'] = 'low'
                analysis['suggestions'].append("Few results found - consider alternative terms")
            
            else:
                # Check result relevance scores
                avg_score = sum(r.get('similarity_score', 0) for r in search_results) / len(search_results)
                
                if avg_score > 0.8:
                    analysis['performance_score'] = 0.9
                    analysis['result_quality'] = 'excellent'
                elif avg_score > 0.6:
                    analysis['performance_score'] = 0.7
                    analysis['result_quality'] = 'good'
                else:
                    analysis['performance_score'] = 0.5
                    analysis['result_quality'] = 'medium'
                    analysis['suggestions'].append("Results have moderate relevance - try more specific terms")
            
            # Intent-based analysis
            intent = self._extract_query_intent(query)
            
            if intent['complexity'] == 'simple' and len(search_results) > 10:
                analysis['optimization_opportunities'].append("Query too broad - add specific constraints")
            
            if not intent['legal_concepts']:
                analysis['optimization_opportunities'].append("Add legal terminology for better precision")
            
            # User feedback analysis
            if user_feedback:
                if user_feedback.get('rating', 0) < 3:
                    analysis['suggestions'].append("Query may need refinement based on user feedback")
                elif user_feedback.get('rating', 0) >= 4:
                    analysis['performance_score'] = min(analysis['performance_score'] + 0.2, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing query performance: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get query optimization statistics"""
        
        return {
            'cache_size': len(self._optimization_cache),
            'cache_hit_rate': 'Not implemented',  # Would track in production
            'avg_optimization_time': 'Not implemented',  # Would track in production
            'most_common_intents': 'Not implemented',  # Would track in production
            'optimization_patterns': {
                'legal_synonyms': len(self.legal_synonyms),
                'expansion_patterns': len(self.expansion_patterns),
                'complexity_levels': len(self.complexity_indicators)
            }
        }
