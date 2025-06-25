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
