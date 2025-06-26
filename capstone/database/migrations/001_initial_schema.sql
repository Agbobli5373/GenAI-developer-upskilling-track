-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create enum types
CREATE TYPE user_role AS ENUM ('Legal Admin', 'Lawyer', 'Paralegal', 'Client');
CREATE TYPE document_type AS ENUM ('contract', 'agreement', 'policy', 'regulation', 'other');
CREATE TYPE document_status AS ENUM ('uploaded', 'processing', 'processed', 'error');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'Client',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Documents table
CREATE TABLE public.documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type TEXT NOT NULL,
    document_type document_type NOT NULL DEFAULT 'contract',
    status document_status NOT NULL DEFAULT 'uploaded',
    uploaded_by UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Document chunks table for vector embeddings
CREATE TABLE public.document_chunks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- Google Gemini embedding dimension
    start_position INTEGER,
    end_position INTEGER,
    page_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Document analysis table
CREATE TABLE public.document_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    analysis_type TEXT NOT NULL, -- 'clause_extraction', 'compliance_check', etc.
    results JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    created_by UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL
);

-- Document versions table for audit trail
CREATE TABLE public.document_versions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    version_number INTEGER NOT NULL,
    changes JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    created_by UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL
);

-- Document shares table for collaboration
CREATE TABLE public.document_shares (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    shared_with UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    permission_level TEXT NOT NULL DEFAULT 'read', -- 'read', 'write', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    created_by UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    UNIQUE(document_id, shared_with)
);

-- Queries table for search history
CREATE TABLE public.queries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    query_text TEXT NOT NULL,
    results JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_documents_uploaded_by ON public.documents(uploaded_by);
CREATE INDEX idx_documents_status ON public.documents(status);
CREATE INDEX idx_documents_type ON public.documents(document_type);
CREATE INDEX idx_documents_created_at ON public.documents(created_at DESC);

CREATE INDEX idx_document_chunks_document_id ON public.document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON public.document_chunks USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_document_analysis_document_id ON public.document_analysis(document_id);
CREATE INDEX idx_document_analysis_type ON public.document_analysis(analysis_type);

CREATE INDEX idx_document_versions_document_id ON public.document_versions(document_id);
CREATE INDEX idx_document_shares_document_id ON public.document_shares(document_id);
CREATE INDEX idx_document_shares_shared_with ON public.document_shares(shared_with);

CREATE INDEX idx_queries_user_id ON public.queries(user_id);
CREATE INDEX idx_queries_created_at ON public.queries(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER handle_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Row Level Security (RLS) policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.queries ENABLE ROW LEVEL SECURITY;

-- Users can read their own profile and admins can read all
CREATE POLICY "Users can read own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Admins can read all users" ON public.users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'Legal Admin'
        )
    );

-- Users can update their own profile and admins can update any
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can update any user" ON public.users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'Legal Admin'
        )
    );

-- Documents policies
CREATE POLICY "Users can read own documents" ON public.documents
    FOR SELECT USING (uploaded_by = auth.uid());

CREATE POLICY "Users can read shared documents" ON public.documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.document_shares 
            WHERE document_id = id AND shared_with = auth.uid()
        )
    );

CREATE POLICY "Admins can read all documents" ON public.documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'Legal Admin'
        )
    );

CREATE POLICY "Users can insert own documents" ON public.documents
    FOR INSERT WITH CHECK (uploaded_by = auth.uid());

CREATE POLICY "Users can update own documents" ON public.documents
    FOR UPDATE USING (uploaded_by = auth.uid());

CREATE POLICY "Users can delete own documents" ON public.documents
    FOR DELETE USING (uploaded_by = auth.uid());

-- Document chunks inherit document permissions
CREATE POLICY "Users can read document chunks" ON public.document_chunks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.documents 
            WHERE id = document_id AND (
                uploaded_by = auth.uid() OR
                EXISTS (
                    SELECT 1 FROM public.document_shares 
                    WHERE document_id = documents.id AND shared_with = auth.uid()
                ) OR
                EXISTS (
                    SELECT 1 FROM public.users 
                    WHERE id = auth.uid() AND role = 'Legal Admin'
                )
            )
        )
    );

-- Similar policies for other tables...
CREATE POLICY "Users can read document analysis" ON public.document_analysis
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.documents 
            WHERE id = document_id AND (
                uploaded_by = auth.uid() OR
                EXISTS (
                    SELECT 1 FROM public.document_shares 
                    WHERE document_id = documents.id AND shared_with = auth.uid()
                ) OR
                EXISTS (
                    SELECT 1 FROM public.users 
                    WHERE id = auth.uid() AND role = 'Legal Admin'
                )
            )
        )
    );

CREATE POLICY "Users can read own queries" ON public.queries
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own queries" ON public.queries
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Create storage bucket for documents
INSERT INTO storage.buckets (id, name, public) VALUES ('documents', 'documents', false);

-- Storage policies
CREATE POLICY "Users can upload documents" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can read own documents" ON storage.objects
    FOR SELECT USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update own documents" ON storage.objects
    FOR UPDATE USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own documents" ON storage.objects
    FOR DELETE USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Create a function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name, role)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        COALESCE(NEW.raw_user_meta_data->>'role', 'Client')::user_role
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
