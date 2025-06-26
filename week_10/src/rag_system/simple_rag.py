"""
Simple RAG system implementation for testing monitoring and evaluation.
"""

import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import google.generativeai as genai

from ..utils.config import config
from ..utils.logging import rag_logger, query_logger
from ..monitoring.performance_monitor import performance_tracker
from ..evaluation.custom_evaluators import RAGEvaluator


@dataclass
class Document:
    """Document representation."""
    
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    
    documents: List[Document]
    query: str
    similarity_scores: List[float]
    retrieval_time: float


@dataclass
class RAGResponse:
    """Complete RAG response."""
    
    query: str
    response: str
    retrieved_documents: List[Document]
    similarity_scores: List[float]
    generation_time: float
    retrieval_time: float
    total_time: float
    metadata: Dict[str, Any]


class SimpleVectorStore:
    """Simple in-memory vector store for testing."""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, List[float]] = {}
    
    def add_document(self, document: Document):
        """Add document to the store."""
        self.documents[document.id] = document
        if document.embedding:
            self.embeddings[document.id] = document.embedding
    
    def add_documents(self, documents: List[Document]):
        """Add multiple documents."""
        for doc in documents:
            self.add_document(doc)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Simple similarity search (mock implementation)."""
        # This is a simplified implementation for testing
        # In reality, you'd use proper embeddings and similarity calculation
        
        # Mock: return documents based on keyword matching
        results = []
        query_lower = query.lower()
        
        for doc in self.documents.values():
            if any(word in doc.content.lower() for word in query_lower.split()):
                results.append(doc)
        
        return results[:k]
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self.documents)


class SimpleRAGSystem:
    """Simple RAG system for testing monitoring and evaluation."""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self.evaluator = RAGEvaluator()
        
        # Initialize Gemini
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
        
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample documents."""
        
        sample_docs = [
            {
                "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans.",
                "metadata": {"source": "ai_basics", "topic": "artificial_intelligence"}
            },
            {
                "content": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
                "metadata": {"source": "ml_basics", "topic": "machine_learning"}
            },
            {
                "content": "Deep Learning uses neural networks with multiple layers to model and understand complex patterns in data.",
                "metadata": {"source": "dl_basics", "topic": "deep_learning"}
            },
            {
                "content": "Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and human language.",
                "metadata": {"source": "nlp_basics", "topic": "natural_language_processing"}
            },
            {
                "content": "Retrieval-Augmented Generation (RAG) combines retrieval mechanisms with generative models to produce more accurate and contextually relevant responses.",
                "metadata": {"source": "rag_basics", "topic": "retrieval_augmented_generation"}
            }
        ]
        
        documents = []
        for i, doc_data in enumerate(sample_docs):
            doc = Document(
                id=f"doc_{i}",
                content=doc_data["content"],
                metadata=doc_data["metadata"]
            )
            documents.append(doc)
        
        self.vector_store.add_documents(documents)
        
        rag_logger.logger.info(
            "Initialized RAG system with sample data",
            num_documents=len(documents)
        )
    
    def retrieve_documents(self, query: str, top_k: int = 3) -> RetrievalResult:
        """Retrieve relevant documents for a query."""
        
        with performance_tracker.track_retrieval(query, top_k) as metrics:
            start_time = time.time()
            
            # Retrieve documents
            documents = self.vector_store.similarity_search(query, k=top_k)
            
            # Mock similarity scores
            similarity_scores = [0.8 - (i * 0.1) for i in range(len(documents))]
            
            retrieval_time = time.time() - start_time
            
            # Update metrics
            metrics.metadata.update({
                "num_documents_found": len(documents),
                "similarity_scores": similarity_scores
            })
            
            result = RetrievalResult(
                documents=documents,
                query=query,
                similarity_scores=similarity_scores,
                retrieval_time=retrieval_time
            )
              # Log retrieval
            rag_logger.log_retrieval(
                query=query,
                retrieved_docs=[{"id": doc.id, "content": doc.content[:100]} for doc in documents],
                retrieval_time=retrieval_time,
                similarity_scores=similarity_scores
            )
            
            return result
    
    def generate_response(self, query: str, contexts: List[str]) -> str:
        """Generate response using Gemini based on query and contexts."""
        
        if not contexts:
            return "I don't have enough information to answer your question."
        
        try:
            # Prepare context for Gemini
            context_text = "\n\n".join(contexts)
            
            prompt = f"""
            Based on the following context, please answer the user's question accurately and concisely.
            
            Context:
            {context_text}
            
            Question: {query}
              Answer:
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.gemini.temperature,
                    max_output_tokens=config.gemini.max_tokens
                )
            )
            
            return response.text
            
        except Exception as e:
            rag_logger.log_error(e, {"operation": "generate_response", "query": query})
            
            # Fallback to mock response
            response_templates = [
                f"Based on the available information, {query.lower()} relates to the provided context.",
                f"According to the documents, here's what I can tell you about {query.lower()}.",
                f"The relevant information indicates details about {query.lower()}."
            ]
            
            template_idx = hash(query) % len(response_templates)
            return response_templates[template_idx]
    
    def query(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        include_evaluation: bool = True
    ) -> RAGResponse:
        """Process a complete RAG query."""
        
        with performance_tracker.track_query(query, user_id) as query_metrics:
            start_time = time.time()
            
            # Log initial query
            rag_logger.log_query(query, user_id, session_id)
            
            # Retrieve documents
            retrieval_result = self.retrieve_documents(query)
            
            # Generate response
            with performance_tracker.track_generation(
                context_length=sum(len(doc.content) for doc in retrieval_result.documents),
                model="mock_model"
            ) as gen_metrics:
                gen_start = time.time()
                
                contexts = [doc.content for doc in retrieval_result.documents]
                response = self.generate_response(query, contexts)
                
                generation_time = time.time() - gen_start
                
                gen_metrics.metadata.update({
                    "response_length": len(response),
                    "context_length": sum(len(ctx) for ctx in contexts)
                })
            
            # Log generation
            rag_logger.log_generation(
                query=query,
                response=response,
                generation_time=generation_time,
                model_used="mock_model",
                context_length=sum(len(ctx) for ctx in contexts)
            )
            
            total_time = time.time() - start_time
            
            # Create response object
            rag_response = RAGResponse(
                query=query,
                response=response,
                retrieved_documents=retrieval_result.documents,
                similarity_scores=retrieval_result.similarity_scores,
                generation_time=generation_time,
                retrieval_time=retrieval_result.retrieval_time,
                total_time=total_time,
                metadata={
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "num_retrieved_docs": len(retrieval_result.documents)
                }
            )
            
            # Evaluate response if requested
            if include_evaluation:
                with performance_tracker.track_evaluation("RAGEvaluator"):
                    evaluation_result = self.evaluator.evaluate_single(
                        query=query,
                        response=response,
                        contexts=contexts,
                        metadata=rag_response.metadata
                    )
                    
                    rag_response.metadata["evaluation_metrics"] = evaluation_result.metrics
            
            # Log complete interaction
            query_logger.log_complete_interaction(
                query=query,
                response=response,
                retrieved_contexts=contexts,
                metrics=rag_response.metadata.get("evaluation_metrics", {}),
                timings={
                    "retrieval_time": retrieval_result.retrieval_time,
                    "generation_time": generation_time,
                    "total_time": total_time
                },
                user_id=user_id,
                session_id=session_id
            )
            
            return rag_response
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add new documents to the system."""
        
        doc_objects = []
        for i, doc_data in enumerate(documents):
            doc_id = doc_data.get("id", f"doc_{int(time.time())}_{i}")
            doc = Document(
                id=doc_id,
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {})
            )
            doc_objects.append(doc)
        
        self.vector_store.add_documents(doc_objects)
        
        rag_logger.logger.info(
            "Added documents to RAG system",
            num_documents=len(doc_objects)
        )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        
        return {
            "total_documents": self.vector_store.get_document_count(),
            "performance_summary": performance_tracker.get_rag_performance_summary(),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def batch_evaluate(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run batch evaluation on test cases."""
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            query = test_case["query"]
            expected_answer = test_case.get("expected_answer")
            
            # Process query
            response = self.query(query, include_evaluation=True)
            
            # Extract evaluation metrics
            eval_metrics = response.metadata.get("evaluation_metrics", {})
            
            result = {
                "test_case_id": i,
                "query": query,
                "response": response.response,
                "expected_answer": expected_answer,
                "metrics": eval_metrics,
                "performance": {
                    "retrieval_time": response.retrieval_time,
                    "generation_time": response.generation_time,
                    "total_time": response.total_time
                },
                "retrieved_documents": len(response.retrieved_documents)
            }
            
            results.append(result)
            
            rag_logger.logger.info(
                f"Completed batch evaluation {i+1}/{len(test_cases)}",
                overall_quality=eval_metrics.get("overall_quality", 0)
            )
        
        return results


# Global RAG system instance
rag_system = SimpleRAGSystem()
