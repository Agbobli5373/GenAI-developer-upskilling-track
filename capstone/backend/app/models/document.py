from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    POLICY = "policy"
    REGULATION = "regulation"
    OTHER = "other"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class ChunkType(str, Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CLAUSE = "clause"
    DEFINITION = "definition"
    LIST_ITEM = "list_item"


class DocumentPosition(BaseModel):
    """Position information for document chunks"""
    page_number: int
    paragraph_index: int
    char_start: int
    char_end: int
    bbox: Optional[Dict[str, float]] = None


class DocumentChunkBase(BaseModel):
    content: str
    chunk_type: ChunkType = ChunkType.PARAGRAPH
    page_number: int = 1
    paragraph_index: int = 0
    char_start: int = 0
    char_end: int = 0
    bbox: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentChunkResponse(DocumentChunkBase):
    id: str
    document_id: str
    chunk_index: int
    created_at: datetime


class DocumentStructure(BaseModel):
    """Document structure overview"""
    chunk_types: Dict[str, int]
    page_distribution: Dict[int, int]
    total_chunks: int


class ProcessingStats(BaseModel):
    """Document processing statistics"""
    total_pages: Optional[int] = None
    total_paragraphs: Optional[int] = None
    extraction_method: str
    processing_time: Optional[float] = None


class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: DocumentType = DocumentType.CONTRACT


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None


class DocumentResponse(DocumentBase):
    id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    status: DocumentStatus
    uploaded_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    content: Optional[str] = None
    total_chunks: Optional[int] = None
    processing_stats: Optional[dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
