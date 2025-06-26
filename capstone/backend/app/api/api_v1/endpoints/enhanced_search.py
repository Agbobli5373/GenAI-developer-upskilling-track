"""
Enhanced Search API endpoints for Week 5
RAG Enhancement and Query Optimization features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.api.api_v1.endpoints.auth import verify_token
from app.services.enhanced_rag_service import EnhancedLegalRAGService
from app.services.query_optimization_service import QueryOptimizationService
from app.services.search_service import AdvancedLegalSearchService

router = APIRouter()
enhanced_rag_service = EnhancedLegalRAGService()
query_optimizer = QueryOptimizationService()
search_service = AdvancedLegalSearchService()


class EnhancedRAGRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    context_limit: int = 8
    min_similarity: float = 0.7
    include_analysis: bool = True
    enable_cross_reference: bool = True


class QueryOptimizationRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    enable_ai_rewriting: bool = True


class BatchQuestionRequest(BaseModel):
    questions: List[str]
    document_ids: Optional[List[str]] = None
    max_concurrent: int = 3


class QuerySuggestionRequest(BaseModel):
    partial_query: str
    document_context: Optional[List[str]] = None
    limit: int = 5


class QueryPerformanceRequest(BaseModel):
    query: str
    search_results: List[Dict[str, Any]]
    user_feedback: Optional[Dict[str, Any]] = None


@router.post("/enhanced-ask")
async def enhanced_question_answering(
    request: EnhancedRAGRequest,
    current_user_id: str = Depends(verify_token)
):
    """Enhanced RAG question answering with legal intelligence"""
    try:
        response = await enhanced_rag_service.enhanced_question_answering(
            question=request.question,
            document_ids=request.document_ids,
            user_id=current_user_id,
            context_limit=request.context_limit,
            min_similarity=request.min_similarity,
            include_analysis=request.include_analysis,
            enable_cross_reference=request.enable_cross_reference
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced question answering failed: {str(e)}"
        )


@router.post("/optimize-query")
async def optimize_query(
    request: QueryOptimizationRequest,
    current_user_id: str = Depends(verify_token)
):
    """Optimize query for better legal document search"""
    try:
        optimization_result = await query_optimizer.optimize_query(
            query=request.query,
            context=request.context,
            enable_ai_rewriting=request.enable_ai_rewriting
        )
        
        return optimization_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query optimization failed: {str(e)}"
        )


@router.post("/batch-questions")
async def batch_question_processing(
    request: BatchQuestionRequest,
    current_user_id: str = Depends(verify_token)
):
    """Process multiple questions concurrently"""
    try:
        if len(request.questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed per batch"
            )
        
        results = await enhanced_rag_service.batch_question_processing(
            questions=request.questions,
            document_ids=request.document_ids,
            user_id=current_user_id,
            max_concurrent=request.max_concurrent
        )
        
        return {
            "total_questions": len(request.questions),
            "processed_count": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.post("/query-suggestions")
async def get_query_suggestions(
    request: QuerySuggestionRequest,
    current_user_id: str = Depends(verify_token)
):
    """Get intelligent query suggestions"""
    try:
        suggestions = await query_optimizer.get_query_suggestions(
            partial_query=request.partial_query,
            document_context=request.document_context,
            limit=request.limit
        )
        
        return {
            "partial_query": request.partial_query,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )


@router.post("/analyze-query-performance")
async def analyze_query_performance(
    request: QueryPerformanceRequest,
    current_user_id: str = Depends(verify_token)
):
    """Analyze query performance and suggest improvements"""
    try:
        analysis = await query_optimizer.analyze_query_performance(
            query=request.query,
            search_results=request.search_results,
            user_feedback=request.user_feedback
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query performance analysis failed: {str(e)}"
        )


@router.get("/rag-analytics")
async def get_rag_analytics(
    current_user_id: str = Depends(verify_token)
):
    """Get RAG service analytics and performance metrics"""
    try:
        analytics = await enhanced_rag_service.get_rag_analytics(current_user_id)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RAG analytics: {str(e)}"
        )


@router.get("/optimization-stats")
async def get_optimization_stats(
    current_user_id: str = Depends(verify_token)
):
    """Get query optimization statistics"""
    try:
        stats = query_optimizer.get_optimization_stats()
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization stats: {str(e)}"
        )


@router.post("/intelligent-search")
async def intelligent_search(
    query: str = Query(..., description="Search query"),
    document_ids: Optional[List[str]] = Query(None, description="Document IDs to search"),
    auto_optimize: bool = Query(True, description="Automatically optimize query"),
    enable_enhanced_rag: bool = Query(False, description="Use enhanced RAG for answers"),
    limit: int = Query(10, description="Maximum results"),
    current_user_id: str = Depends(verify_token)
):
    """
    Intelligent search that combines query optimization with enhanced search and RAG
    """
    try:
        search_results = {}
        
        # Step 1: Optimize query if requested
        if auto_optimize:
            optimization_result = await query_optimizer.optimize_query(
                query=query,
                enable_ai_rewriting=True
            )
            
            optimized_query = optimization_result.get('optimized_query', query)
            search_results['query_optimization'] = optimization_result
        else:
            optimized_query = query
        
        # Step 2: Perform enhanced search
        advanced_search_results = await search_service.advanced_semantic_search(
            query=optimized_query,
            document_ids=document_ids,
            user_id=current_user_id,
            limit=limit,
            enable_caching=True,
            include_suggestions=True
        )
        
        search_results['search_results'] = advanced_search_results
        
        # Step 3: Enhanced RAG if requested and results found
        if enable_enhanced_rag and advanced_search_results.get('results'):
            rag_response = await enhanced_rag_service.enhanced_question_answering(
                question=query,
                document_ids=document_ids,
                user_id=current_user_id,
                include_analysis=True,
                enable_cross_reference=True
            )
            
            search_results['rag_response'] = rag_response
        
        # Step 4: Compile comprehensive response
        return {
            'original_query': query,
            'optimized_query': optimized_query if auto_optimize else query,
            'search_results': search_results,
            'total_results': advanced_search_results.get('total_results', 0),
            'response_type': 'enhanced_rag' if enable_enhanced_rag else 'search_only',
            'features_used': {
                'query_optimization': auto_optimize,
                'enhanced_rag': enable_enhanced_rag,
                'advanced_search': True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligent search failed: {str(e)}"
        )


@router.get("/legal-concepts")
async def get_legal_concepts(
    current_user_id: str = Depends(verify_token)
):
    """Get available legal concepts for query building"""
    try:
        concepts = {
            'legal_synonyms': query_optimizer.legal_synonyms,
            'expansion_patterns': list(query_optimizer.expansion_patterns.keys()),
            'complexity_levels': list(query_optimizer.complexity_indicators.keys()),
            'question_types': list(enhanced_rag_service.legal_question_patterns.keys())
        }
        
        return concepts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get legal concepts: {str(e)}"
        )


@router.post("/compare-query-strategies")
async def compare_query_strategies(
    original_query: str,
    alternative_queries: List[str],
    document_ids: Optional[List[str]] = None,
    current_user_id: str = Depends(verify_token)
):
    """Compare different query strategies and their effectiveness"""
    try:
        if len(alternative_queries) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 alternative queries allowed"
            )
        
        # Test all queries
        all_queries = [original_query] + alternative_queries
        results = {}
        
        for i, query in enumerate(all_queries):
            query_key = 'original' if i == 0 else f'alternative_{i}'
            
            # Search with each query
            search_result = await search_service.advanced_semantic_search(
                query=query,
                document_ids=document_ids,
                user_id=current_user_id,
                limit=10,
                enable_caching=False  # Don't cache comparison results
            )
            
            results[query_key] = {
                'query': query,
                'total_results': search_result.get('total_results', 0),
                'avg_similarity': 0,
                'top_score': 0
            }
            
            # Calculate metrics
            if search_result.get('results'):
                scores = [r.get('similarity_score', 0) for r in search_result['results']]
                results[query_key]['avg_similarity'] = sum(scores) / len(scores)
                results[query_key]['top_score'] = max(scores)
        
        # Determine best strategy
        best_query = max(results.keys(), key=lambda k: results[k]['avg_similarity'])
        
        return {
            'comparison_results': results,
            'best_strategy': best_query,
            'recommendation': f"Query '{results[best_query]['query']}' performed best with {results[best_query]['total_results']} results and {results[best_query]['avg_similarity']:.3f} average similarity"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query strategy comparison failed: {str(e)}"
        )
