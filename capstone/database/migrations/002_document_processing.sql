-- Week 2: Document Processing Tables
-- This migration adds support for document processing with positional information

-- Add new columns to documents table for processing
ALTER TABLE documents ADD COLUMN IF NOT EXISTS content TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_stats JSONB;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS total_chunks INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Create document_chunks table for storing parsed content with positions
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    chunk_type VARCHAR(50) NOT NULL DEFAULT 'paragraph',
    page_number INTEGER NOT NULL DEFAULT 1,
    paragraph_index INTEGER NOT NULL DEFAULT 0,
    char_start INTEGER NOT NULL DEFAULT 0,
    char_end INTEGER NOT NULL DEFAULT 0,
    bbox JSONB, -- Bounding box for PDF positioning
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(document_id, chunk_index),
    CHECK (char_end >= char_start),
    CHECK (page_number > 0),
    CHECK (paragraph_index >= 0)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_type ON document_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_document_chunks_page_number ON document_chunks(page_number);
CREATE INDEX IF NOT EXISTS idx_document_chunks_content_search ON document_chunks USING gin(to_tsvector('english', content));

-- Add RLS policies for document_chunks
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access chunks from their own documents
CREATE POLICY "Users can access chunks from their own documents" ON document_chunks
    FOR ALL USING (
        document_id IN (
            SELECT id FROM documents 
            WHERE uploaded_by = auth.uid()::text
        )
    );

-- Policy: Legal admins can access all chunks
CREATE POLICY "Legal admins can access all chunks" ON document_chunks
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE auth.uid() = id 
            AND raw_user_meta_data->>'role' = 'legal_admin'
        )
    );

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);

-- Add constraint to ensure valid statuses
ALTER TABLE documents ADD CONSTRAINT valid_status 
    CHECK (status IN ('uploaded', 'processing', 'processed', 'error'));

-- Add constraint to ensure valid document types
ALTER TABLE documents ADD CONSTRAINT valid_document_type 
    CHECK (document_type IN ('contract', 'agreement', 'policy', 'regulation', 'other'));

-- Add function to automatically update document updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for documents table
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE document_chunks IS 'Stores parsed document content with positional information for clause identification';
COMMENT ON COLUMN document_chunks.chunk_type IS 'Type of content: paragraph, heading, clause, definition, list_item';
COMMENT ON COLUMN document_chunks.bbox IS 'Bounding box coordinates for PDF positioning (x, y, width, height)';
COMMENT ON COLUMN document_chunks.char_start IS 'Character position start in the full document text';
COMMENT ON COLUMN document_chunks.char_end IS 'Character position end in the full document text';

-- Grant necessary permissions
GRANT ALL ON document_chunks TO authenticated;
GRANT ALL ON document_chunks TO service_role;
