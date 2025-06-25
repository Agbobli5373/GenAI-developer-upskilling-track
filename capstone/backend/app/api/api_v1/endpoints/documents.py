from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
import uuid
from datetime import datetime

from app.api.api_v1.endpoints.auth import verify_token
from app.core.database import supabase
from app.models.document import DocumentResponse, DocumentCreate, DocumentUpdate

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    document_type: Optional[str] = None,
    current_user_id: str = Depends(verify_token)
):
    """Upload a document"""
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
