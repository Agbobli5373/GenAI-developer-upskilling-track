"""
Document Storage Service

Handles storage and retrieval of processed document data including 
chunks, positions, and metadata in Supabase.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import supabase
from app.services.document_processor import ProcessedDocument, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentStorageService:
    """Service for storing and retrieving processed document data"""
    
    def __init__(self):
        pass
    
    async def store_processed_document(
        self,
        processed_doc: ProcessedDocument,
        user_id: str
    ) -> bool:
        """
        Store processed document and its chunks in the database
        
        Args:
            processed_doc: The processed document data
            user_id: ID of the user who owns the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update document status and add processed content
            document_update = {
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat(),
                "content": processed_doc.content,
                "metadata": json.dumps(processed_doc.metadata),
                "processing_stats": json.dumps(processed_doc.processing_stats),
                "total_chunks": len(processed_doc.chunks)
            }
            
            # Update the main document record
            doc_result = supabase.table("documents").update(document_update).eq(
                "id", processed_doc.document_id
            ).execute()
            
            if not doc_result.data:
                logger.error(f"Failed to update document {processed_doc.document_id}")
                return False
            
            # Store document chunks
            await self._store_document_chunks(processed_doc.chunks, processed_doc.document_id)
            
            logger.info(f"Successfully stored processed document {processed_doc.document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing processed document {processed_doc.document_id}: {str(e)}")
            return False
    
    async def _store_document_chunks(
        self,
        chunks: List[DocumentChunk],
        document_id: str
    ) -> bool:
        """Store document chunks in the database"""
        try:
            chunk_data = []
            
            for idx, chunk in enumerate(chunks):
                chunk_record = {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "content": chunk.text,
                    "chunk_type": chunk.chunk_type,
                    "page_number": chunk.position.page_number,
                    "paragraph_index": chunk.position.paragraph_index,
                    "char_start": chunk.position.char_start,
                    "char_end": chunk.position.char_end,
                    "metadata": json.dumps(chunk.metadata),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Add bounding box if available (for PDFs)
                if chunk.position.bbox:
                    chunk_record["bbox"] = json.dumps(chunk.position.bbox)
                
                chunk_data.append(chunk_record)
            
            # Batch insert chunks
            if chunk_data:
                result = supabase.table("document_chunks").insert(chunk_data).execute()
                if result.data:
                    logger.info(f"Stored {len(chunk_data)} chunks for document {document_id}")
                    return True
                else:
                    logger.error(f"Failed to store chunks for document {document_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing chunks for document {document_id}: {str(e)}")
            return False
    
    async def get_document_chunks(
        self,
        document_id: str,
        chunk_type: Optional[str] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve document chunks with optional filtering
        
        Args:
            document_id: The document ID
            chunk_type: Filter by chunk type (optional)
            page_number: Filter by page number (optional)
            
        Returns:
            List of document chunks
        """
        try:
            query = supabase.table("document_chunks").select("*").eq("document_id", document_id)
            
            if chunk_type:
                query = query.eq("chunk_type", chunk_type)
                
            if page_number:
                query = query.eq("page_number", page_number)
            
            result = query.order("chunk_index").execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error retrieving chunks for document {document_id}: {str(e)}")
            return []
    
    async def get_document_content(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get the full processed document content"""
        try:
            result = supabase.table("documents").select("*").eq("id", document_id).execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None
    
    async def search_chunks_by_text(
        self,
        document_id: str,
        search_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks containing specific text
        
        Args:
            document_id: The document ID
            search_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching chunks
        """
        try:
            # Use Supabase's text search functionality
            result = supabase.table("document_chunks").select("*").eq(
                "document_id", document_id
            ).ilike("content", f"%{search_text}%").limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching chunks in document {document_id}: {str(e)}")
            return []
    
    async def get_document_structure(self, document_id: str) -> Dict[str, Any]:
        """
        Get document structure overview
        
        Args:
            document_id: The document ID
            
        Returns:
            Document structure information
        """
        try:
            # Get chunk type distribution
            result = supabase.table("document_chunks").select(
                "chunk_type, page_number, count(*)"
            ).eq("document_id", document_id).execute()
            
            if not result.data:
                return {}
            
            # Organize structure data
            structure = {
                "chunk_types": {},
                "page_distribution": {},
                "total_chunks": 0
            }
            
            for row in result.data:
                chunk_type = row.get("chunk_type", "unknown")
                page_num = row.get("page_number", 1)
                count = row.get("count", 0)
                
                structure["chunk_types"][chunk_type] = structure["chunk_types"].get(chunk_type, 0) + count
                structure["page_distribution"][page_num] = structure["page_distribution"].get(page_num, 0) + count
                structure["total_chunks"] += count
            
            return structure
            
        except Exception as e:
            logger.error(f"Error getting structure for document {document_id}: {str(e)}")
            return {}
    
    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update document processing status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            result = supabase.table("documents").update(update_data).eq(
                "id", document_id
            ).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating status for document {document_id}: {str(e)}")
            return False
