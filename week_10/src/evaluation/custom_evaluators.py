"""
Custom evaluation metrics for RAG systems.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from ..utils.config import config
from ..utils.logging import rag_logger


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    
    query: str
    response: str
    contexts: List[str]
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: str


class RelevancyEvaluator:
    """Evaluates relevancy of retrieved documents to queries."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.retrieval.embedding_model)
    
    def evaluate(self, query: str, contexts: List[str]) -> float:
        """Calculate relevancy score between query and contexts."""
        if not contexts:
            return 0.0
        
        try:
            # Get embeddings
            query_embedding = self.embedding_model.encode([query])
            context_embeddings = self.embedding_model.encode(contexts)
            
            # Calculate similarities - convert to numpy arrays first
            query_emb = np.array(query_embedding)
            context_emb = np.array(context_embeddings)
            
            similarities = np.dot(query_emb, context_emb.T)[0]
            
            # Return average similarity as relevancy score
            return float(np.mean(similarities))
            
        except Exception as e:
            rag_logger.log_error(e, {"evaluator": "relevancy", "query": query})
            return 0.0


class FaithfulnessEvaluator:
    """Evaluates faithfulness of response to retrieved contexts."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
    
    def evaluate(self, response: str, contexts: List[str]) -> float:
        """Evaluate how faithful the response is to the provided contexts."""
        if not contexts or not response:
            return 0.0
        
        context_text = "\n\n".join(contexts)
        
        prompt = f"""
        Evaluate how faithful the following response is to the provided context.
        Rate from 0.0 (completely unfaithful) to 1.0 (completely faithful).
        Only respond with a number.
        
        Context:
        {context_text}
        
        Response:
        {response}
          Faithfulness Score:
        """
        
        try:
            response_obj = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=10
                )
            )
            
            score_text = response_obj.text.strip()
            return float(score_text)
            
        except Exception as e:
            rag_logger.log_error(e, {"evaluator": "faithfulness", "response_preview": response[:100]})
            return 0.0


class AnswerRelevanceEvaluator:
    """Evaluates how well the answer addresses the original question."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
        self.embedding_model = SentenceTransformer(config.retrieval.embedding_model)
    
    def evaluate(self, query: str, response: str) -> float:
        """Evaluate answer relevance using semantic similarity."""
        if not query or not response:
            return 0.0
        
        try:
            # Method 1: Semantic similarity
            query_embedding = self.embedding_model.encode([query])
            response_embedding = self.embedding_model.encode([response])
            
            # Convert to numpy arrays and calculate similarity
            query_emb = np.array(query_embedding)
            response_emb = np.array(response_embedding)
            
            similarity = np.dot(query_emb, response_emb.T)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            rag_logger.log_error(e, {"evaluator": "answer_relevance", "query": query})
            return 0.0


class HallucinationDetector:
    """Detects hallucinations in RAG responses."""
    
    def __init__(self):
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
    
    def evaluate(self, query: str, response: str, contexts: List[str]) -> float:
        """Detect hallucinations in the response. Returns hallucination score (0-1)."""
        if not contexts or not response:
            return 1.0  # No context means potential hallucination
        
        context_text = "\n\n".join(contexts)
        
        prompt = f"""
        Analyze the following response to determine if it contains hallucinations 
        (information not supported by the provided context).
        
        Rate from 0.0 (no hallucinations) to 1.0 (completely hallucinated).
        Only respond with a number.
        
        Query: {query}
        
        Context:
        {context_text}
        
        Response:
        {response}
          Hallucination Score:
        """
        
        try:
            response_obj = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=10
                )
            )
            
            score_text = response_obj.text.strip()
            return float(score_text)
            
        except Exception as e:
            rag_logger.log_error(e, {"evaluator": "hallucination", "query": query})
            return 0.5  # Return neutral score on error


class ContextPrecisionEvaluator:
    """Evaluates precision of retrieved contexts."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.retrieval.embedding_model)
    
    def evaluate(self, query: str, contexts: List[str]) -> float:
        """Calculate context precision - how many retrieved docs are relevant."""
        if not contexts:
            return 0.0
        
        try:
            query_embedding = self.embedding_model.encode([query])
            context_embeddings = self.embedding_model.encode(contexts)
            
            # Convert to numpy arrays
            query_emb = np.array(query_embedding)
            context_emb = np.array(context_embeddings)
            
            similarities = np.dot(query_emb, context_emb.T)[0]
            
            # Consider contexts with similarity > threshold as relevant
            threshold = 0.3
            relevant_count = np.sum(similarities > threshold)
            
            precision = relevant_count / len(contexts)
            return float(precision)
            
        except Exception as e:
            rag_logger.log_error(e, {"evaluator": "context_precision", "query": query})
            return 0.0


class RAGEvaluator:
    """Main evaluator that orchestrates all evaluation metrics."""
    
    def __init__(self):
        self.relevancy_evaluator = RelevancyEvaluator()
        self.faithfulness_evaluator = FaithfulnessEvaluator()
        self.answer_relevance_evaluator = AnswerRelevanceEvaluator()
        self.hallucination_detector = HallucinationDetector()
        self.context_precision_evaluator = ContextPrecisionEvaluator()
    
    def evaluate_single(
        self,
        query: str,
        response: str,
        contexts: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """Evaluate a single RAG interaction."""
        
        start_time = time.time()
        
        metrics = {}
        
        # Run all evaluations
        metrics['relevancy'] = self.relevancy_evaluator.evaluate(query, contexts)
        metrics['faithfulness'] = self.faithfulness_evaluator.evaluate(response, contexts)
        metrics['answer_relevance'] = self.answer_relevance_evaluator.evaluate(query, response)
        metrics['hallucination_score'] = self.hallucination_detector.evaluate(query, response, contexts)
        metrics['context_precision'] = self.context_precision_evaluator.evaluate(query, contexts)
        
        # Calculate composite scores
        metrics['overall_quality'] = (
            metrics['relevancy'] * 0.3 +
            metrics['faithfulness'] * 0.3 +
            metrics['answer_relevance'] * 0.2 +
            (1 - metrics['hallucination_score']) * 0.2
        )
        
        evaluation_time = time.time() - start_time
        
        result = EvaluationResult(
            query=query,
            response=response,
            contexts=contexts,
            metrics=metrics,
            metadata={
                'evaluation_time': evaluation_time,
                'num_contexts': len(contexts),
                **(metadata or {})
            },
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Log the evaluation
        rag_logger.log_evaluation(
            query=query,
            response=response,
            metrics=metrics,
            evaluator="RAGEvaluator"
        )
        
        return result
    
    def evaluate_batch(
        self,
        queries: List[str],
        responses: List[str],
        contexts_list: List[List[str]],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[EvaluationResult]:
        """Evaluate a batch of RAG interactions."""
        
        if not (len(queries) == len(responses) == len(contexts_list)):
            raise ValueError("All input lists must have the same length")
        
        results = []
        metadata_list = metadata_list or [{}] * len(queries)
        
        for i, (query, response, contexts, metadata) in enumerate(
            zip(queries, responses, contexts_list, metadata_list)
        ):
            try:
                result = self.evaluate_single(query, response, contexts, metadata)
                results.append(result)
                
                rag_logger.logger.info(
                    f"Evaluated batch item {i+1}/{len(queries)}",
                    overall_quality=result.metrics['overall_quality']
                )
                
            except Exception as e:
                rag_logger.log_error(e, {
                    "batch_index": i,
                    "query": query[:100],
                    "evaluator": "batch_evaluation"
                })
                
        return results
    
    def get_summary_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Calculate summary statistics from evaluation results."""
        if not results:
            return {}
        
        metrics_names = list(results[0].metrics.keys())
        summary = {}
        
        for metric_name in metrics_names:
            values = [result.metrics[metric_name] for result in results]
            summary[f"{metric_name}_mean"] = np.mean(values)
            summary[f"{metric_name}_std"] = np.std(values)
            summary[f"{metric_name}_min"] = np.min(values)
            summary[f"{metric_name}_max"] = np.max(values)
        
        summary['total_evaluations'] = len(results)
        summary['avg_evaluation_time'] = np.mean([
            result.metadata.get('evaluation_time', 0) for result in results
        ])
        
        return summary
