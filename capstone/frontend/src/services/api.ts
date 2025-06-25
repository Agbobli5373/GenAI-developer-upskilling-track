import axios, { AxiosResponse } from 'axios'
import { User, UserCreate, UserLogin, AuthResponse, Document, DocumentCreate, DocumentUpdate } from '@/types'

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
export const authAPI = {
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
export const usersAPI = {
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
export const documentsAPI = {
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
}

export default api
