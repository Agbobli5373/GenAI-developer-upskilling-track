from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

from app.api.api_v1.endpoints.auth import verify_token
from app.core.database import supabase
from app.models.document import (
    DocumentResponse, DocumentCreate, DocumentUpdate, 
    DocumentChunkResponse, DocumentStructure
)
from app.services.document_processor import DocumentProcessor
from app.services.document_storage import DocumentStorageService

router = APIRouter()
document_processor = DocumentProcessor()
document_storage = DocumentStorageService()


async def process_document_background(
    document_id: str,
    file_content: bytes,
    filename: str,
    file_type: str,
    user_id: str
):
    """Background task to process uploaded documents"""
    try:
        # Update status to processing
        await document_storage.update_document_status(document_id, "processing")
        
        # Process the document
        processed_doc = await document_processor.process_document(
            file_content=file_content,
            filename=filename,
            document_id=document_id,
            file_type=file_type
        )
        
        # Store processed document
        success = await document_storage.store_processed_document(processed_doc, user_id)
        
        if not success:
            await document_storage.update_document_status(
                document_id, "error", "Failed to store processed document"
            )
        
    except Exception as e:
        # Update status to error
        await document_storage.update_document_status(
            document_id, "error", str(e)
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    document_type: Optional[str] = None,
    current_user_id: str = Depends(verify_token)
):
    """Upload a document with automatic processing"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx', 'txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not supported. Only PDF, DOCX, and TXT files are allowed."
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{file_extension}"
        
        # Read file content
        content = await file.read()
        
        # Upload to Supabase Storage
        storage_response = supabase.storage.from_("documents").upload(filename, content)
        
        if storage_response.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
        
        # Create document record
        document_data = {
            "id": file_id,
            "title": title or file.filename,
            "description": description,
            "filename": file.filename,
            "file_path": filename,
            "file_size": len(content),
            "file_type": file_extension,
            "document_type": document_type or "contract",
            "uploaded_by": current_user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "uploaded"
        }
        
        result = supabase.table("documents").insert(document_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create document record"
            )
        
        # Start background processing
        background_tasks.add_task(
            process_document_background,
            file_id,
            content,
            file.filename,
            file_extension,
            current_user_id
        )
        
        return DocumentResponse(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = None,
    current_user_id: str = Depends(verify_token)
):
    """Get user's documents"""
    try:
        query = supabase.table("documents").select("*").eq("uploaded_by", current_user_id)
        
        if document_type:
            query = query.eq("document_type", document_type)
        
        result = query.range(skip, skip + limit - 1).execute()
        
        return [DocumentResponse(**doc) for doc in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, current_user_id: str = Depends(verify_token)):
    """Get document by ID"""
    try:
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = result.data[0]
        
        # Check if user has access to this document
        if document["uploaded_by"] != current_user_id:
            # Check if user is admin or has shared access
            current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
            if not current_user.data or current_user.data[0]["role"] != "Legal Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        
        return DocumentResponse(**document)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user_id: str = Depends(verify_token)
):
    """Update document metadata"""
    try:
        # Check if document exists and user has access
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = result.data[0]
        
        if document["uploaded_by"] != current_user_id:
            current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
            if not current_user.data or current_user.data[0]["role"] != "Legal Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        
        # Update document
        update_data = document_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            result = supabase.table("documents").update(update_data).eq("id", document_id).execute()
            return DocumentResponse(**result.data[0])
        
        return DocumentResponse(**document)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user_id: str = Depends(verify_token)):
    """Delete document"""
    try:
        # Check if document exists and user has access
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = result.data[0]
        
        if document["uploaded_by"] != current_user_id:
            current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
            if not current_user.data or current_user.data[0]["role"] != "Legal Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        
        # Delete from storage
        storage_response = supabase.storage.from_("documents").remove([document["file_path"]])
        
        # Delete document record
        supabase.table("documents").delete().eq("id", document_id).execute()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse])
async def get_document_chunks(
    document_id: str,
    chunk_type: Optional[str] = None,
    page_number: Optional[int] = None,
    current_user_id: str = Depends(verify_token)
):
    """Get chunks for a specific document"""
    try:
        # Verify document ownership
        doc = await document_storage.get_document_content(document_id)
        if not doc or doc["uploaded_by"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        chunks = await document_storage.get_document_chunks(
            document_id, chunk_type, page_number
        )
        
        return [DocumentChunkResponse(**chunk) for chunk in chunks]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document chunks: {str(e)}"
        )


@router.get("/{document_id}/structure", response_model=DocumentStructure)
async def get_document_structure(
    document_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get document structure overview"""
    try:
        # Verify document ownership
        doc = await document_storage.get_document_content(document_id)
        if not doc or doc["uploaded_by"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        structure = await document_storage.get_document_structure(document_id)
        
        return DocumentStructure(**structure)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document structure: {str(e)}"
        )


@router.get("/{document_id}/search")
async def search_document_chunks(
    document_id: str,
    q: str,
    limit: int = 10,
    current_user_id: str = Depends(verify_token)
):
    """Search for text within a document"""
    try:
        # Verify document ownership
        doc = await document_storage.get_document_content(document_id)
        if not doc or doc["uploaded_by"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        chunks = await document_storage.search_chunks_by_text(document_id, q, limit)
        
        return {
            "query": q,
            "document_id": document_id,
            "total_results": len(chunks),
            "chunks": chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(verify_token)
):
    """Reprocess a document (useful after processing improvements)"""
    try:
        # Get document info
        doc = await document_storage.get_document_content(document_id)
        if not doc or doc["uploaded_by"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get original file from storage
        file_response = supabase.storage.from_("documents").download(doc["file_path"])
        
        if not file_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve original file"
            )
        
        # Clear existing chunks
        supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
        
        # Start reprocessing
        background_tasks.add_task(
            process_document_background,
            document_id,
            file_response,
            doc["filename"],
            doc["file_type"],
            current_user_id
        )
        
        return {"message": "Document reprocessing started", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reprocessing failed: {str(e)}"
        )
