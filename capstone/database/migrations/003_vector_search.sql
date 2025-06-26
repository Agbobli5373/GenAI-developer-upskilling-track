-- Week 3: Vector Search Foundation
-- This migration adds support for vector embeddings and semantic search

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding columns to document_chunks table
ALTER TABLE document_chunks 
ADD COLUMN IF NOT EXISTS embedding vector(768),  -- Gemini embedding dimension
ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100),
ADD COLUMN IF NOT EXISTS embedding_created_at TIMESTAMP WITH TIME ZONE;

-- Add embedding tracking columns to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS embedding_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS embedded_chunks INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS embedding_error TEXT;

-- Create vector similarity index for efficient search
-- Using ivfflat index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine 
ON document_chunks USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create additional index for combined queries
CREATE INDEX IF NOT EXISTS idx_document_chunks_composite 
ON document_chunks(document_id, chunk_type, embedding) 
WHERE embedding IS NOT NULL;

-- Add constraint for valid embedding statuses
ALTER TABLE documents ADD CONSTRAINT IF NOT EXISTS valid_embedding_status 
    CHECK (embedding_status IN ('pending', 'processing', 'embedded', 'embedding_error'));

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(768),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_document_ids uuid[] DEFAULT NULL,
    target_chunk_types text[] DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    chunk_type text,
    page_number int,
    similarity_score float,
    document_title text,
    document_filename text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        dc.content,
        dc.chunk_type,
        dc.page_number,
        1 - (dc.embedding <-> query_embedding) as similarity_score,
        d.title as document_title,
        d.filename as document_filename
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE dc.embedding IS NOT NULL
        AND 1 - (dc.embedding <-> query_embedding) >= similarity_threshold
        AND (target_document_ids IS NULL OR dc.document_id = ANY(target_document_ids))
        AND (target_chunk_types IS NULL OR dc.chunk_type = ANY(target_chunk_types))
    ORDER BY dc.embedding <-> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create function for hybrid search (vector + keyword)
CREATE OR REPLACE FUNCTION hybrid_search_chunks(
    query_text text,
    query_embedding vector(768),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_document_ids uuid[] DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    chunk_type text,
    page_number int,
    similarity_score float,
    keyword_rank float,
    combined_score float,
    document_title text
) AS $$
BEGIN
    RETURN QUERY
    WITH vector_search AS (
        SELECT 
            dc.id,
            dc.document_id,
            dc.content,
            dc.chunk_type,
            dc.page_number,
            1 - (dc.embedding <-> query_embedding) as similarity_score,
            0::float as keyword_rank,
            d.title as document_title
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE dc.embedding IS NOT NULL
            AND 1 - (dc.embedding <-> query_embedding) >= similarity_threshold
            AND (target_document_ids IS NULL OR dc.document_id = ANY(target_document_ids))
    ),
    keyword_search AS (
        SELECT 
            dc.id,
            dc.document_id,
            dc.content,
            dc.chunk_type,
            dc.page_number,
            0::float as similarity_score,
            ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', query_text)) as keyword_rank,
            d.title as document_title
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE to_tsvector('english', dc.content) @@ plainto_tsquery('english', query_text)
            AND (target_document_ids IS NULL OR dc.document_id = ANY(target_document_ids))
    ),
    combined AS (
        SELECT 
            COALESCE(v.id, k.id) as id,
            COALESCE(v.document_id, k.document_id) as document_id,
            COALESCE(v.content, k.content) as content,
            COALESCE(v.chunk_type, k.chunk_type) as chunk_type,
            COALESCE(v.page_number, k.page_number) as page_number,
            COALESCE(v.similarity_score, 0) as similarity_score,
            COALESCE(k.keyword_rank, 0) as keyword_rank,
            (COALESCE(v.similarity_score, 0) * 0.7 + COALESCE(k.keyword_rank, 0) * 0.3) as combined_score,
            COALESCE(v.document_title, k.document_title) as document_title
        FROM vector_search v
        FULL OUTER JOIN keyword_search k ON v.id = k.id
    )
    SELECT * FROM combined
    ORDER BY combined_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create search analytics table for tracking search performance
CREATE TABLE IF NOT EXISTS search_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    query TEXT NOT NULL,
    query_type VARCHAR(50) DEFAULT 'semantic',
    results_count INTEGER DEFAULT 0,
    avg_similarity_score FLOAT,
    search_time FLOAT,
    document_filters TEXT[],
    chunk_type_filters TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for search analytics
CREATE INDEX IF NOT EXISTS idx_search_analytics_user_id ON search_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_search_analytics_created_at ON search_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_search_analytics_query_type ON search_analytics(query_type);

-- Add RLS for search analytics
ALTER TABLE search_analytics ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own search analytics
CREATE POLICY "Users can access their own search analytics" ON search_analytics
    FOR ALL USING (user_id = auth.uid()::text);

-- Policy: Legal admins can access all search analytics
CREATE POLICY "Legal admins can access all search analytics" ON search_analytics
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE auth.uid() = id 
            AND raw_user_meta_data->>'role' = 'legal_admin'
        )
    );

-- Create function to update embedding statistics
CREATE OR REPLACE FUNCTION update_document_embedding_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update document embedding stats when chunks are updated
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE documents 
        SET embedded_chunks = (
            SELECT COUNT(*) 
            FROM document_chunks 
            WHERE document_id = NEW.document_id 
            AND embedding IS NOT NULL
        ),
        embedding_updated_at = NOW()
        WHERE id = NEW.document_id;
        
        RETURN NEW;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        UPDATE documents 
        SET embedded_chunks = (
            SELECT COUNT(*) 
            FROM document_chunks 
            WHERE document_id = OLD.document_id 
            AND embedding IS NOT NULL
        ),
        embedding_updated_at = NOW()
        WHERE id = OLD.document_id;
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic embedding stats updates
DROP TRIGGER IF EXISTS update_embedding_stats_trigger ON document_chunks;
CREATE TRIGGER update_embedding_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_embedding_stats();

-- Add performance optimization indexes
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_not_null 
ON document_chunks(document_id) WHERE embedding IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_documents_embedding_status 
ON documents(embedding_status);

-- Add function for embedding health check
CREATE OR REPLACE FUNCTION get_embedding_health()
RETURNS TABLE (
    total_documents bigint,
    documents_with_embeddings bigint,
    total_chunks bigint,
    embedded_chunks bigint,
    embedding_coverage_percent numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM documents)::bigint as total_documents,
        (SELECT COUNT(*) FROM documents WHERE embedded_chunks > 0)::bigint as documents_with_embeddings,
        (SELECT COUNT(*) FROM document_chunks)::bigint as total_chunks,
        (SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL)::bigint as embedded_chunks,
        CASE 
            WHEN (SELECT COUNT(*) FROM document_chunks) > 0 
            THEN ROUND((SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL)::numeric / 
                      (SELECT COUNT(*) FROM document_chunks)::numeric * 100, 2)
            ELSE 0::numeric
        END as embedding_coverage_percent;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT ALL ON search_analytics TO authenticated;
GRANT ALL ON search_analytics TO service_role;
GRANT EXECUTE ON FUNCTION search_similar_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION hybrid_search_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION get_embedding_health TO authenticated;

-- Add comments for documentation
COMMENT ON COLUMN document_chunks.embedding IS 'Vector embedding for semantic search (768 dimensions for Gemini)';
COMMENT ON COLUMN document_chunks.embedding_model IS 'Model used to generate the embedding';
COMMENT ON COLUMN documents.embedding_status IS 'Status of embedding generation: pending, processing, embedded, embedding_error';
COMMENT ON FUNCTION search_similar_chunks IS 'Performs vector similarity search using cosine distance';
COMMENT ON FUNCTION hybrid_search_chunks IS 'Combines vector similarity and keyword search with weighted scoring';
COMMENT ON TABLE search_analytics IS 'Tracks search queries and performance metrics for analytics';

-- Create view for embedding analytics
CREATE OR REPLACE VIEW embedding_analytics AS
SELECT 
    d.id as document_id,
    d.title,
    d.document_type,
    d.embedding_status,
    d.embedded_chunks,
    d.total_chunks,
    CASE 
        WHEN d.total_chunks > 0 
        THEN ROUND(d.embedded_chunks::numeric / d.total_chunks::numeric * 100, 2)
        ELSE 0::numeric
    END as embedding_completion_percent,
    d.embedding_updated_at,
    d.created_at
FROM documents d
ORDER BY d.embedding_updated_at DESC NULLS LAST;
