import axios, { AxiosResponse } from 'axios'
import {
    User, UserCreate, UserLogin, AuthResponse, Document, DocumentCreate, DocumentUpdate,
    DocumentChunk, DocumentStructure, DocumentSearchResult,
    SearchResponse,
    ComparisonResult,
    RAGResponse,
    EnhancedRAGResponse,
    QueryOptimizationResponse,
    QuerySuggestion,
    QueryPerformanceAnalysis,
    IntelligentSearchResponse,
    BatchQuestionResponse,
    EnhancedRAGRequest,
    QueryOptimizationRequest,
    IntelligentSearchRequest,
    BatchQuestionRequest
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

// Auth API
const authAPI = {
    register: (userData: UserCreate): Promise<AxiosResponse<User>> =>
        api.post('/auth/register', userData),

    login: (credentials: UserLogin): Promise<AxiosResponse<AuthResponse>> =>
        api.post('/auth/login', credentials),

    logout: (): Promise<AxiosResponse<{ message: string }>> =>
        api.post('/auth/logout'),

    getCurrentUser: (): Promise<AxiosResponse<User>> =>
        api.get('/auth/me'),
}

// Users API
const usersAPI = {
    getUsers: (): Promise<AxiosResponse<User[]>> =>
        api.get('/users'),

    getUser: (userId: string): Promise<AxiosResponse<User>> =>
        api.get(`/users/${userId}`),

    updateUser: (userId: string, userData: Partial<User>): Promise<AxiosResponse<User>> =>
        api.put(`/users/${userId}`, userData),

    deleteUser: (userId: string): Promise<AxiosResponse<{ message: string }>> =>
        api.delete(`/users/${userId}`),
}

// Documents API
const documentsAPI = {
    uploadDocument: (file: File, metadata?: Partial<DocumentCreate>): Promise<AxiosResponse<Document>> => {
        const formData = new FormData()
        formData.append('file', file)

        if (metadata?.title) formData.append('title', metadata.title)
        if (metadata?.description) formData.append('description', metadata.description)
        if (metadata?.document_type) formData.append('document_type', metadata.document_type)

        return api.post('/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },

    getDocuments: (params?: { skip?: number; limit?: number; document_type?: string }): Promise<AxiosResponse<Document[]>> =>
        api.get('/documents', { params }),

    getDocument: (documentId: string): Promise<AxiosResponse<Document>> =>
        api.get(`/documents/${documentId}`),

    updateDocument: (documentId: string, data: DocumentUpdate): Promise<AxiosResponse<Document>> =>
        api.put(`/documents/${documentId}`, data),

    deleteDocument: (documentId: string): Promise<AxiosResponse<{ message: string }>> =>
        api.delete(`/documents/${documentId}`),

    // New document processing endpoints
    getDocumentChunks: (
        documentId: string,
        params?: { chunk_type?: string; page_number?: number }
    ): Promise<AxiosResponse<DocumentChunk[]>> =>
        api.get(`/documents/${documentId}/chunks`, { params }),

    getDocumentStructure: (documentId: string): Promise<AxiosResponse<DocumentStructure>> =>
        api.get(`/documents/${documentId}/structure`),

    searchDocumentChunks: (
        documentId: string,
        query: string,
        limit?: number
    ): Promise<AxiosResponse<DocumentSearchResult>> =>
        api.get(`/documents/${documentId}/search`, {
            params: { q: query, limit }
        }),

    reprocessDocument: (documentId: string): Promise<AxiosResponse<{ message: string; document_id: string }>> =>
        api.post(`/documents/${documentId}/reprocess`),

    // Advanced search endpoints
    advancedSearch: (params: {
        query: string;
        document_ids?: string[];
        search_filters?: Record<string, any>;
        limit?: number;
        enable_query_expansion?: boolean;
        enable_reranking?: boolean;
    }): Promise<AxiosResponse<SearchResponse>> =>
        api.post('/search/advanced-search', params),

    multiDocumentComparison: (params: {
        document_ids: string[];
        comparison_type?: string;
        analysis_depth?: string;
    }): Promise<AxiosResponse<ComparisonResult>> =>
        api.post('/search/multi-document-comparison', params),

    getSearchSuggestions: (query: string, limit?: number): Promise<AxiosResponse<{ suggestions: string[] }>> =>
        api.get('/search/suggestions', { params: { q: query, limit } }),

    // Existing search endpoints
    semanticSearch: (params: {
        query: string;
        document_ids?: string[];
        chunk_types?: string[];
        limit?: number;
        similarity_threshold?: number;
        include_hybrid?: boolean;
    }): Promise<AxiosResponse<SearchResponse>> =>
        api.post('/search/semantic-search', params),

    askQuestion: (params: {
        question: string;
        document_ids?: string[];
        context_limit?: number;
        min_similarity?: number;
        include_analysis?: boolean;
    }): Promise<AxiosResponse<RAGResponse>> =>
        api.post('/search/ask', params),

    // Week 5: Enhanced RAG and Query Optimization Endpoints
    enhancedRAGSearch: (params: EnhancedRAGRequest): Promise<AxiosResponse<EnhancedRAGResponse>> =>
        api.post('/enhanced-search/rag', params),

    optimizeQuery: (params: QueryOptimizationRequest): Promise<AxiosResponse<QueryOptimizationResponse>> =>
        api.post('/enhanced-search/optimize-query', params),

    getQuerySuggestions: (query: string): Promise<AxiosResponse<{ suggestions: QuerySuggestion[] }>> =>
        api.get('/enhanced-search/query-suggestions', { params: { query } }),

    analyzeQueryPerformance: (params: { query: string }): Promise<AxiosResponse<QueryPerformanceAnalysis>> =>
        api.post('/enhanced-search/analyze-query-performance', params),

    intelligentSearch: (params: IntelligentSearchRequest): Promise<AxiosResponse<IntelligentSearchResponse>> =>
        api.post('/enhanced-search/intelligent-search', params),

    batchQuestionProcessing: (params: BatchQuestionRequest): Promise<AxiosResponse<BatchQuestionResponse>> =>
        api.post('/enhanced-search/batch-questions', params),
}

// Combined API service
export const apiService = {
    ...authAPI,
    ...usersAPI,
    ...documentsAPI,

    // Add search methods with proper naming
    advancedSearch: (params: {
        query: string;
        document_ids?: string[];
        search_filters?: Record<string, any>;
        limit?: number;
        enable_query_expansion?: boolean;
        enable_reranking?: boolean;
    }): Promise<AxiosResponse<SearchResponse>> =>
        documentsAPI.advancedSearch(params),

    multiDocumentComparison: (params: {
        document_ids: string[];
        comparison_type?: string;
        analysis_depth?: string;
    }): Promise<AxiosResponse<ComparisonResult>> =>
        documentsAPI.multiDocumentComparison(params),

    getSearchSuggestions: (query: string, limit?: number): Promise<AxiosResponse<{ suggestions: string[] }>> =>
        documentsAPI.getSearchSuggestions(query, limit),

    semanticSearch: (params: {
        query: string;
        document_ids?: string[];
        chunk_types?: string[];
        limit?: number;
        similarity_threshold?: number;
        include_hybrid?: boolean;
    }): Promise<AxiosResponse<SearchResponse>> =>
        documentsAPI.semanticSearch(params),

    askQuestion: (params: {
        question: string;
        document_ids?: string[];
        context_limit?: number;
        min_similarity?: number;
        include_analysis?: boolean;
    }): Promise<AxiosResponse<RAGResponse>> =>
        documentsAPI.askQuestion(params),

    // Week 5: Enhanced RAG and Query Optimization methods
    enhancedRAGSearch: (params: EnhancedRAGRequest): Promise<AxiosResponse<EnhancedRAGResponse>> =>
        api.post('/enhanced-search/rag', params),

    optimizeQuery: (params: QueryOptimizationRequest): Promise<AxiosResponse<QueryOptimizationResponse>> =>
        api.post('/enhanced-search/optimize-query', params),

    getQuerySuggestions: (query: string): Promise<AxiosResponse<{ suggestions: QuerySuggestion[] }>> =>
        api.get('/enhanced-search/query-suggestions', { params: { query } }),

    analyzeQueryPerformance: (params: { query: string }): Promise<AxiosResponse<QueryPerformanceAnalysis>> =>
        api.post('/enhanced-search/analyze-query-performance', params),

    intelligentSearch: (params: IntelligentSearchRequest): Promise<AxiosResponse<IntelligentSearchResponse>> =>
        api.post('/enhanced-search/intelligent-search', params),

    batchQuestionProcessing: (params: BatchQuestionRequest): Promise<AxiosResponse<BatchQuestionResponse>> =>
        api.post('/enhanced-search/batch-questions', params),
}

export { authAPI, usersAPI, documentsAPI }
export default api
