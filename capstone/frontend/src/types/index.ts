export interface User {
    id: string
    email: string
    full_name: string
    role: 'Legal Admin' | 'Lawyer' | 'Paralegal' | 'Client'
    is_active: boolean
    created_at: string
    updated_at?: string
}

export interface UserCreate {
    email: string
    password: string
    full_name: string
    role: 'Legal Admin' | 'Lawyer' | 'Paralegal' | 'Client'
}

export interface UserLogin {
    email: string
    password: string
}

export interface AuthResponse {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
}

export interface Document {
    id: string
    title: string
    description?: string
    filename: string
    file_path: string
    file_size: number
    file_type: string
    document_type: 'contract' | 'agreement' | 'policy' | 'regulation' | 'other'
    status: 'uploaded' | 'processing' | 'processed' | 'error'
    uploaded_by: string
    created_at: string
    updated_at?: string
    processed_at?: string
    content?: string
    total_chunks?: number
    processing_stats?: ProcessingStats
    error_message?: string
}

export interface DocumentChunk {
    id: string
    document_id: string
    chunk_index: number
    content: string
    chunk_type: 'paragraph' | 'heading' | 'clause' | 'definition' | 'list_item'
    page_number: number
    paragraph_index: number
    char_start: number
    char_end: number
    bbox?: BoundingBox
    metadata?: Record<string, any>
    created_at: string
}

export interface BoundingBox {
    x: number
    y: number
    width: number
    height: number
}

export interface DocumentStructure {
    chunk_types: Record<string, number>
    page_distribution: Record<number, number>
    total_chunks: number
}

export interface ProcessingStats {
    total_pages?: number
    total_paragraphs?: number
    extraction_method: string
    processing_time?: number
}

export interface DocumentSearchResult {
    query: string
    document_id: string
    total_results: number
    chunks: DocumentChunk[]
}

export interface DocumentCreate {
    title: string
    description?: string
    document_type: 'contract' | 'agreement' | 'policy' | 'regulation' | 'other'
}

export interface DocumentUpdate {
    title?: string
    description?: string
    document_type?: 'contract' | 'agreement' | 'policy' | 'regulation' | 'other'
}

export interface ApiError {
    detail: string
}

// Search and RAG Types
export interface SearchResult {
    id: string
    document_id: string
    document_title: string
    document_type: string
    content: string
    chunk_type: string
    page_number: number
    similarity_score?: number
    keyword_rank?: number
    combined_score?: number
    enhanced_score?: number
    source?: 'vector' | 'keyword' | 'hybrid'
    metadata?: Record<string, any>
}

export interface SearchResponse {
    query: string
    results: SearchResult[]
    total_results: number
    search_time: number
    enhanced_scoring_used?: boolean
    query_expanded?: boolean
    suggestions?: string[]
    error?: string
}

export interface RAGResponse {
    question: string
    answer: string
    confidence: number
    sources: SearchResult[]
    analysis?: {
        query_type: string
        legal_concepts: string[]
        entities: string[]
    }
    context_used: number
    response_time: number
}

export interface ComparisonResult {
    comparison_type: string
    document_count: number
    similarities?: Array<{
        documents: string[]
        similarity_score: number
        common_terms: string[]
    }>
    differences?: Array<{
        document: string
        unique_terms: string[]
        uniqueness_score: number
    }>
    coverage_analysis?: {
        total_documents: number
        topic_distribution: Record<string, Record<string, number>>
        coverage_gaps: string[]
    }
}

export interface QueryIntent {
    type: 'definition' | 'procedure' | 'temporal' | 'general'
    legal_concepts: string[]
    entities: string[]
    confidence: number
}

export interface SearchAnalytics {
    total_searches: number
    popular_queries: Array<{
        query: string
        count: number
    }>
    avg_search_time: number
    search_patterns: Record<string, number>
    user_activity: Record<string, number>
}

// Week 5: Enhanced RAG and Query Optimization Types

export interface EnhancedRAGResponse {
    query: string
    answer: string
    confidence_score?: number
    sources: Array<{
        document_id: string
        title: string
        content: string
        relevance_score: number
        page_number: number
        chunk_type: string
    }>
    legal_analysis?: {
        key_legal_concepts: string[]
        jurisdictions: string[]
        risk_factors: string[]
        compliance_requirements: string[]
    }
    cross_references?: Array<{
        title: string
        description: string
        relationship_type: string
        relevance_score: number
    }>
    context_optimization?: {
        context_used: number
        context_available: number
        optimization_strategy: string
    }
    metadata?: {
        processing_time: number
        tokens_used: number
        model_version: string
    }
}

export interface QueryOptimizationResponse {
    original_query: string
    optimized_query: string
    optimization_type: string
    explanation: string
    suggested_refinements?: string[]
    legal_context?: {
        identified_concepts: string[]
        suggested_jurisdictions: string[]
        practice_areas: string[]
    }
    performance_prediction?: {
        expected_improvement: number
        complexity_reduction: number
    }
}

export interface QuerySuggestion {
    query: string
    confidence: number
    explanation?: string
    intent_type?: string
    legal_concepts?: string[]
}

export interface QueryPerformanceAnalysis {
    query: string
    complexity_score: number
    clarity_score: number
    specificity_score: number
    overall_score: number
    identified_issues: string[]
    improvement_suggestions: string[]
    legal_domain_alignment?: number
    expected_result_quality?: number
}

export interface IntelligentSearchResponse {
    query: string
    rag_response: EnhancedRAGResponse
    optimization?: QueryOptimizationResponse
    performance?: QueryPerformanceAnalysis
    search_strategy: string
    total_processing_time: number
}

export interface BatchQuestionResponse {
    batch_id: string
    total_questions: number
    completed: number
    results: Array<{
        question: string
        answer: EnhancedRAGResponse
        processing_time: number
        success: boolean
        error?: string
    }>
    batch_summary: {
        total_processing_time: number
        success_rate: number
        common_themes: string[]
    }
}

// Enhanced search request types

export interface EnhancedRAGRequest {
    query: string
    document_ids?: string[]
    max_results?: number
    optimize_query?: boolean
    include_legal_analysis?: boolean
    include_cross_references?: boolean
    context_optimization?: boolean
}

export interface QueryOptimizationRequest {
    query: string
    context?: string
    optimization_type?: 'legal' | 'semantic' | 'performance' | 'comprehensive'
    target_domain?: string
}

export interface IntelligentSearchRequest {
    query: string
    document_ids?: string[]
    use_optimization?: boolean
    max_results?: number
    search_strategy?: 'balanced' | 'comprehensive' | 'fast'
}

export interface BatchQuestionRequest {
    questions: string[]
    document_ids?: string[]
    batch_settings?: {
        max_parallel: number
        timeout_per_question: number
        include_cross_references: boolean
    }
}
