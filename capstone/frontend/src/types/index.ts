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
