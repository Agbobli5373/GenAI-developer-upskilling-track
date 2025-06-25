"""
Search API endpoints for legal document semantic search and RAG
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.api.api_v1.endpoints.auth import verify_token
from app.services.search_service import LegalSearchService
from app.services.rag_service import LegalRAGService
from app.services.embedding_service import LegalEmbeddingService

router = APIRouter()
search_service = LegalSearchService()
rag_service = LegalRAGService()
embedding_service = LegalEmbeddingService()


class SearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    chunk_types: Optional[List[str]] = None
    limit: int = 10
    similarity_threshold: float = 0.7
    include_hybrid: bool = True


class RAGRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    context_limit: int = 5
    min_similarity: float = 0.7
    include_analysis: bool = True


class EmbeddingRequest(BaseModel):
    document_ids: List[str]
    batch_size: int = 20


@router.post("/semantic-search")
async def semantic_search(
    request: SearchRequest,
    current_user_id: str = Depends(verify_token)
):
    """Perform semantic search across legal documents"""
    try:
        results = await search_service.semantic_search(
            query=request.query,
            document_ids=request.document_ids,
            chunk_types=request.chunk_types,
            user_id=current_user_id,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold,
            include_hybrid=request.include_hybrid
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/ask")
async def ask_question(
    request: RAGRequest,
    current_user_id: str = Depends(verify_token)
):
    """Ask a question about legal documents using RAG"""
    try:
        response = await rag_service.answer_legal_question(
            question=request.question,
            document_ids=request.document_ids,
            user_id=current_user_id,
            context_limit=request.context_limit,
            min_similarity=request.min_similarity,
            include_analysis=request.include_analysis
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions"),
    current_user_id: str = Depends(verify_token)
):
    """Get search suggestions based on partial query"""
    try:
        suggestions = await search_service.search_suggestions(q, limit)
        
        return {
            "partial_query": q,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.post("/embeddings/generate")
async def generate_embeddings(
    background_tasks: BackgroundTasks,
    request: EmbeddingRequest,
    current_user_id: str = Depends(verify_token)
):
    """Generate embeddings for specified documents"""
    try:
        # Verify user owns the documents
        from app.core.database import supabase
        
        for doc_id in request.document_ids:
            result = supabase.table("documents").select("uploaded_by").eq("id", doc_id).execute()
            
            if not result.data or result.data[0]["uploaded_by"] != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to document {doc_id}"
                )
        
        # Start background embedding generation
        for doc_id in request.document_ids:
            background_tasks.add_task(
                embedding_service.generate_embeddings_for_document,
                doc_id,
                request.batch_size
            )
        
        return {
            "message": f"Embedding generation started for {len(request.document_ids)} documents",
            "document_ids": request.document_ids,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start embedding generation: {str(e)}"
        )


@router.get("/embeddings/status")
async def get_embedding_status(
    document_id: Optional[str] = Query(None, description="Specific document ID"),
    current_user_id: str = Depends(verify_token)
):
    """Get embedding generation status"""
    try:
        if document_id:
            # Verify user owns the document
            from app.core.database import supabase
            result = supabase.table("documents").select("uploaded_by").eq("id", document_id).execute()
            
            if not result.data or result.data[0]["uploaded_by"] != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to document"
                )
        
        stats = await embedding_service.get_embedding_stats(document_id)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embedding status: {str(e)}"
        )


@router.get("/analytics")
async def get_search_analytics(
    current_user_id: str = Depends(verify_token)
):
    """Get search analytics and insights"""
    try:
        analytics = await search_service.get_search_analytics(current_user_id)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.post("/documents/{document_id}/summary")
async def generate_document_summary(
    document_id: str,
    summary_type: str = Query("comprehensive", description="Type of summary: comprehensive, executive, or brief"),
    current_user_id: str = Depends(verify_token)
):
    """Generate AI summary of a legal document"""
    try:
        # Verify user owns the document
        from app.core.database import supabase
        result = supabase.table("documents").select("uploaded_by").eq("id", document_id).execute()
        
        if not result.data or result.data[0]["uploaded_by"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to document"
            )
        
        summary = await rag_service.generate_document_summary(
            document_id=document_id,
            user_id=current_user_id,
            summary_type=summary_type
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/health")
async def search_health_check():
    """Health check for search services"""
    try:
        # Check embedding coverage
        stats = await embedding_service.get_embedding_stats()
        
        health_status = {
            "status": "healthy",
            "embedding_coverage": stats.get("embedding_coverage", 0),
            "embedded_chunks": stats.get("embedded_chunks", 0),
            "total_chunks": stats.get("total_chunks", 0),
            "services": {
                "search_service": "active",
                "rag_service": "active", 
                "embedding_service": "active"
            }
        }
        
        # Determine overall health
        if stats.get("embedded_chunks", 0) == 0:
            health_status["status"] = "degraded"
            health_status["message"] = "No embeddings available - search functionality limited"
        elif stats.get("embedding_coverage", 0) < 50:
            health_status["status"] = "warning"
            health_status["message"] = "Low embedding coverage - some content may not be searchable"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "search_service": "error",
                "rag_service": "error",
                "embedding_service": "error"
            }
        }
