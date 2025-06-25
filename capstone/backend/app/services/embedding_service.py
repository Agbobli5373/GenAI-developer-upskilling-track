"""
Legal Document Embedding Service

This service handles embedding generation for legal documents using a combination of
text processing and vector generation techniques for semantic search and RAG.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import hashlib
import json

from app.core.config import settings
from app.core.database import supabase
from app.services.document_storage import DocumentStorageService

logger = logging.getLogger(__name__)


class LegalEmbeddingService:
    """Service for generating and managing legal document embeddings"""
    
    def __init__(self):
        # For now, we'll use a simple approach to generate embeddings
        # In production, you would use proper embedding models like:
        # - OpenAI embeddings
        # - Sentence Transformers
        # - Hugging Face models
        
        self.embedding_dimension = settings.EMBEDDING_DIMENSION
        self.legal_context = """
        This content is from legal documents including contracts, agreements, policies, and regulations.
        Focus on legal concepts, clauses, obligations, definitions, and contractual relationships.
        """
        
        self.document_storage = DocumentStorageService()
        
        # Legal keywords for enhanced embedding
        self.legal_keywords = [
            'agreement', 'contract', 'clause', 'obligation', 'liability', 'terms',
            'conditions', 'warranty', 'indemnification', 'breach', 'termination',
            'confidentiality', 'intellectual property', 'damages', 'jurisdiction',
            'governing law', 'force majeure', 'assignment', 'modification'
        ]
    
    async def generate_embeddings_for_document(
        self, 
        document_id: str,
        batch_size: int = 20
    ) -> bool:
        """
        Generate embeddings for all chunks of a document
        
        Args:
            document_id: The document to process
            batch_size: Number of chunks to process at once
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Generating embeddings for document {document_id}")
            
            # Get document chunks
            chunks = await self.document_storage.get_document_chunks(document_id)
            
            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return False
            
            # Process chunks in batches
            total_chunks = len(chunks)
            processed = 0
            
            for i in range(0, total_chunks, batch_size):
                batch_chunks = chunks[i:i + batch_size]
                
                # Generate embeddings for batch
                embeddings = await self._generate_batch_embeddings(batch_chunks)
                
                if embeddings:
                    # Store embeddings in database
                    await self._store_chunk_embeddings(batch_chunks, embeddings)
                    processed += len(batch_chunks)
                    
                    logger.info(f"Processed {processed}/{total_chunks} chunks for document {document_id}")
            
            # Update document status
            await self._update_document_embedding_status(document_id, "embedded", processed)
            
            logger.info(f"Successfully generated embeddings for {processed} chunks in document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating embeddings for document {document_id}: {str(e)}")
            await self._update_document_embedding_status(document_id, "embedding_error", 0, str(e))
            return False
    
    async def _generate_batch_embeddings(
        self, 
        chunks: List[Dict[str, Any]]
    ) -> Optional[List[List[float]]]:
        """Generate embeddings for a batch of chunks using text-based features"""
        try:
            # Generate embeddings for each chunk
            embeddings = []
            
            for chunk in chunks:
                try:
                    # Enhanced text with legal context
                    enhanced_text = f"""
                    {self.legal_context}
                    
                    Content Type: {chunk.get('chunk_type', 'paragraph')}
                    Legal Document Content: {chunk['content']}
                    """
                    
                    embedding = self._generate_text_embedding(enhanced_text.strip())
                    embeddings.append(embedding)
                    
                    # Small delay for rate limiting
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"Error generating single embedding: {str(e)}")
                    embeddings.append(None)
            
            # Filter out None embeddings
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            
            if len(valid_embeddings) != len(chunks):
                logger.warning(f"Generated {len(valid_embeddings)} embeddings for {len(chunks)} chunks")
            
            return valid_embeddings if valid_embeddings else None
            
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {str(e)}")
            return None
    
    def _generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate a simple text-based embedding vector
        
        In production, replace this with proper embedding models like:
        - OpenAI embeddings
        - Sentence Transformers
        - Hugging Face models
        """
        try:
            # Normalize text
            text_lower = text.lower()
            
            # Create features based on text characteristics
            features = []
            
            # 1. Text length features (normalized)
            features.extend([
                min(len(text) / 1000.0, 1.0),  # Text length
                min(len(text.split()) / 100.0, 1.0),  # Word count
                min(len(text.split('.')) / 20.0, 1.0),  # Sentence count
            ])
            
            # 2. Legal keyword presence
            for keyword in self.legal_keywords:
                features.append(1.0 if keyword in text_lower else 0.0)
            
            # 3. Character-based features
            features.extend([
                text_lower.count(',') / max(len(text), 1),  # Comma density
                text_lower.count(';') / max(len(text), 1),  # Semicolon density
                text_lower.count('(') / max(len(text), 1),  # Parentheses density
                text_lower.count('"') / max(len(text), 1),  # Quote density
            ])
            
            # 4. Word-based features
            words = text_lower.split()
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                features.append(min(avg_word_length / 10.0, 1.0))
            else:
                features.append(0.0)
            
            # 5. Hash-based features for content similarity
            text_hash = hashlib.md5(text.encode()).hexdigest()
            hash_features = []
            for i in range(0, min(32, len(text_hash)), 2):
                hash_features.append(int(text_hash[i:i+2], 16) / 255.0)
            
            features.extend(hash_features)
            
            # Pad or truncate to desired dimension
            while len(features) < self.embedding_dimension:
                features.append(0.0)
            
            features = features[:self.embedding_dimension]
            
            # Normalize the vector
            magnitude = sum(f * f for f in features) ** 0.5
            if magnitude > 0:
                features = [f / magnitude for f in features]
            
            return features
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def _store_chunk_embeddings(
        self, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> bool:
        """Store embeddings in the database"""
        try:
            updates = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is not None:
                    updates.append({
                        "id": chunk["id"],
                        "embedding": embedding,
                        "embedding_model": "text-features-v1",
                        "embedding_created_at": datetime.utcnow().isoformat()
                    })
            
            if updates:
                # Batch update chunks with embeddings
                for update in updates:
                    supabase.table("document_chunks").update({
                        "embedding": update["embedding"],
                        "embedding_model": update["embedding_model"],
                        "embedding_created_at": update["embedding_created_at"]
                    }).eq("id", update["id"]).execute()
                
                logger.info(f"Stored {len(updates)} embeddings in database")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error storing chunk embeddings: {str(e)}")
            return False
    
    async def _update_document_embedding_status(
        self, 
        document_id: str, 
        status: str, 
        embedded_chunks: int,
        error_message: Optional[str] = None
    ):
        """Update document embedding status"""
        try:
            update_data = {
                "embedding_status": status,
                "embedded_chunks": embedded_chunks,
                "embedding_updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data["embedding_error"] = error_message
            
            supabase.table("documents").update(update_data).eq("id", document_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating document embedding status: {str(e)}")
    
    async def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for a search query
        
        Args:
            query: The search query text
            
        Returns:
            Query embedding vector or None if failed
        """
        try:
            # Enhance query with legal context
            enhanced_query = f"""
            {self.legal_context}
            
            Legal Query: {query}
            """
            
            # Generate embedding using our simple method
            embedding = self._generate_text_embedding(enhanced_query.strip())
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return None
    
    async def find_similar_chunks(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None,
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find chunks similar to query embedding using vector similarity
        
        Args:
            query_embedding: The query embedding vector
            document_ids: Optional filter by document IDs
            chunk_types: Optional filter by chunk types
            similarity_threshold: Minimum similarity score
            limit: Maximum number of results
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            # Build the SQL query for vector similarity search
            query_vector = str(query_embedding)
            
            sql_query = f"""
                SELECT 
                    dc.*,
                    d.title as document_title,
                    d.filename as document_filename,
                    1 - (dc.embedding <-> '{query_vector}'::vector) as similarity_score
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE dc.embedding IS NOT NULL
            """
            
            # Add filters
            params = []
            
            if document_ids:
                placeholders = ','.join([f"'{doc_id}'" for doc_id in document_ids])
                sql_query += f" AND dc.document_id IN ({placeholders})"
            
            if chunk_types:
                placeholders = ','.join([f"'{chunk_type}'" for chunk_type in chunk_types])
                sql_query += f" AND dc.chunk_type IN ({placeholders})"
            
            sql_query += f"""
                AND 1 - (dc.embedding <-> '{query_vector}'::vector) >= {similarity_threshold}
                ORDER BY dc.embedding <-> '{query_vector}'::vector
                LIMIT {limit}
            """
            
            # Execute the query
            result = supabase.rpc('exec_sql', {'query': sql_query}).execute()
            
            if result.data and result.data[0].get('result'):
                return result.data[0]['result']
            
            return []
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            return []
    
    async def get_embedding_stats(self, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Get embedding statistics"""
        try:
            if document_id:
                # Stats for specific document
                result = supabase.table("document_chunks").select(
                    "id, embedding"
                ).eq("document_id", document_id).execute()
            else:
                # Global stats
                result = supabase.table("document_chunks").select(
                    "id, embedding, document_id"
                ).execute()
            
            if not result.data:
                return {"total_chunks": 0, "embedded_chunks": 0, "embedding_coverage": 0.0}
            
            total_chunks = len(result.data)
            embedded_chunks = len([chunk for chunk in result.data if chunk.get("embedding")])
            
            coverage = (embedded_chunks / total_chunks * 100) if total_chunks > 0 else 0
            
            stats = {
                "total_chunks": total_chunks,
                "embedded_chunks": embedded_chunks,
                "embedding_coverage": round(coverage, 2)
            }
            
            if document_id:
                stats["document_id"] = document_id
            else:
                # Add document-level breakdown
                doc_stats = {}
                for chunk in result.data:
                    doc_id = chunk["document_id"]
                    if doc_id not in doc_stats:
                        doc_stats[doc_id] = {"total": 0, "embedded": 0}
                    doc_stats[doc_id]["total"] += 1
                    if chunk.get("embedding"):
                        doc_stats[doc_id]["embedded"] += 1
                
                stats["documents"] = doc_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting embedding stats: {str(e)}")
            return {"error": str(e)}
