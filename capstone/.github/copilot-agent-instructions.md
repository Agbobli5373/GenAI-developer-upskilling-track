# Copilot Agent Instructions for Clause Intelligence System

## Overview

This document provides comprehensive instructions for a Copilot agent to implement the **Clause Intelligence System** - an AI-powered legal document analysis platform using **Python (FastAPI)**, **Supabase**, and **Vite React (TypeScript)**.

## Project Context: Clause Intelligence System

The Clause Intelligence System helps legal professionals efficiently analyze, manage, and update contractual agreements through:

- Advanced document parsing with positional tracking
- Semantic search across legal documents
- Precise clause identification and amendment workflows
- AI agents for compliance checking and multi-step legal analysis
- Comprehensive audit trails for legal compliance

## Primary Tech Stack

### Core Technologies

- **Backend**: Python with FastAPI framework
- **Frontend**: React with TypeScript using Vite
- **Database**: Supabase (PostgreSQL with pgvector for embeddings)
- **LLM Integration**: Google Gemini API (1.5 Pro for complex reasoning, Flash for speed)
- **Authentication**: Supabase Auth with Row Level Security (RLS)
- **Document Processing**: PDF.js, python-docx, pytesseract for OCR
- **Vector Operations**: Supabase pgvector extension

## Core Application Components

### 1. Legal Document Management & Processing System

#### Architecture Requirements

- **Backend**: FastAPI with async document processing
- **Frontend**: React TypeScript with document viewers (PDF.js, custom DOCX viewer)
- **Storage**: Supabase Storage for original documents + PostgreSQL for parsed content
- **Processing**: Multi-format document parsing with positional information
- **Security**: Role-based access for legal professionals

#### Implementation Guidelines

**Backend Structure (FastAPI):**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── models/
│   │   ├── __init__.py
│   │   ├── auth.py          # User and role models
│   │   ├── documents.py     # Legal document models
│   │   ├── clauses.py       # Clause and amendment models
│   │   └── agents.py        # AI agent request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Authentication logic
│   │   ├── document_processor.py # PDF/DOCX parsing with positions
│   │   ├── embedding_service.py # Legal-aware embeddings
│   │   ├── search_service.py     # Legal document search
│   │   ├── clause_service.py     # Clause identification & amendments
│   │   ├── agent_service.py      # AI agents for legal analysis
│   │   └── compliance_service.py # Compliance checking
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── documents.py     # Document upload/management
│   │   ├── search.py        # Legal search endpoints
│   │   ├── clauses.py       # Clause management
│   │   ├── agents.py        # AI agent endpoints
│   │   └── compliance.py    # Compliance checking
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── document_parser.py   # PDF/DOCX parsing utilities
│   │   ├── legal_chunking.py    # Legal-aware text chunking
│   │   ├── position_mapper.py   # Document position tracking
│   │   └── legal_prompts.py     # Legal-specific prompt templates
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Base agent class
│   │   ├── query_agent.py       # Multi-step query agent
│   │   ├── compliance_agent.py  # Compliance checking agent
│   │   └── amendment_agent.py   # Amendment suggestion agent
│   ├── config.py            # Configuration management
│   └── database.py          # Supabase setup
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── alembic.ini             # Database migration config
```

**Key Components to Implement:**

1. **Legal Document Database Schema**

   ```sql
   -- Enable pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;

   -- Legal documents table with metadata
   CREATE TABLE legal_documents (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       title TEXT NOT NULL,
       document_type TEXT NOT NULL CHECK (document_type IN ('contract', 'policy', 'law', 'regulation')),
       file_path TEXT NOT NULL, -- Path to original document in Supabase Storage
       parsed_content TEXT NOT NULL,
       metadata JSONB DEFAULT '{}', -- parties, dates, jurisdiction, etc.
       structure_map JSONB DEFAULT '{}', -- sections, paragraphs, page mapping
       created_by UUID REFERENCES auth.users(id),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Document chunks with legal-aware embeddings
   CREATE TABLE document_chunks (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       document_id UUID REFERENCES legal_documents(id) ON DELETE CASCADE,
       chunk_content TEXT NOT NULL,
       embedding vector(1536), -- Google Gemini embedding size
       chunk_type TEXT CHECK (chunk_type IN ('paragraph', 'clause', 'section', 'article')),
       position_info JSONB NOT NULL, -- page, paragraph_index, bounding_box
       legal_metadata JSONB DEFAULT '{}', -- clause_type, importance, references
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Clause amendments tracking
   CREATE TABLE clause_amendments (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       document_id UUID REFERENCES legal_documents(id),
       original_chunk_id UUID REFERENCES document_chunks(id),
       original_text TEXT NOT NULL,
       amended_text TEXT NOT NULL,
       amendment_reason TEXT,
       amendment_type TEXT CHECK (amendment_type IN ('update', 'delete', 'add')),
       status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
       created_by UUID REFERENCES auth.users(id),
       approved_by UUID REFERENCES auth.users(id),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       approved_at TIMESTAMP WITH TIME ZONE
   );

   -- Compliance issues tracking
   CREATE TABLE compliance_issues (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       document_id UUID REFERENCES legal_documents(id),
       chunk_id UUID REFERENCES document_chunks(id),
       issue_type TEXT NOT NULL,
       severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
       description TEXT NOT NULL,
       recommendation TEXT,
       status TEXT DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'ignored')),
       created_by UUID REFERENCES auth.users(id),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create vector similarity index
   CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);

   -- Row Level Security policies for legal documents
   ALTER TABLE legal_documents ENABLE ROW LEVEL SECURITY;
   ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
   ALTER TABLE clause_amendments ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Legal professionals can access documents based on role"
   ON legal_documents FOR ALL
   USING (
       auth.jwt() ->> 'role' IN ('legal_admin', 'senior_lawyer') OR
       (auth.jwt() ->> 'role' = 'lawyer' AND created_by = auth.uid()) OR
       (auth.jwt() ->> 'role' = 'paralegal' AND
        document_type IN ('policy', 'regulation'))
   );
   ```

2. **Document Processing Service**

   ```python
   # services/document_processor.py
   from typing import Dict, List, Any, Tuple
   import PyPDF2
   import pytesseract
   from PIL import Image
   from docx import Document
   from pdf2image import convert_from_path
   import json

   class LegalDocumentProcessor:
       def __init__(self):
           self.supported_formats = ['.pdf', '.docx', '.txt']

       async def process_document(
           self,
           file_path: str,
           document_type: str
       ) -> Dict[str, Any]:
           """Process legal document and extract content with positions"""

           file_extension = file_path.lower().split('.')[-1]

           if file_extension == 'pdf':
               return await self._process_pdf(file_path, document_type)
           elif file_extension == 'docx':
               return await self._process_docx(file_path, document_type)
           elif file_extension == 'txt':
               return await self._process_txt(file_path, document_type)
           else:
               raise ValueError(f"Unsupported file format: {file_extension}")

       async def _process_pdf(self, file_path: str, doc_type: str) -> Dict[str, Any]:
           """Extract text from PDF with positional information"""

           content_blocks = []
           structure_map = {"pages": [], "sections": []}

           with open(file_path, 'rb') as file:
               pdf_reader = PyPDF2.PdfReader(file)

               for page_num, page in enumerate(pdf_reader.pages):
                   try:
                       # Extract text with basic positioning
                       text = page.extract_text()
                       paragraphs = self._split_into_paragraphs(text)

                       page_info = {
                           "page_number": page_num + 1,
                           "paragraphs": []
                       }

                       for para_idx, paragraph in enumerate(paragraphs):
                           if paragraph.strip():
                               content_blocks.append({
                                   "content": paragraph,
                                   "page": page_num + 1,
                                   "paragraph_index": para_idx,
                                   "type": self._classify_paragraph(paragraph, doc_type)
                               })

                               page_info["paragraphs"].append({
                                   "index": para_idx,
                                   "content": paragraph[:100] + "...",
                                   "type": self._classify_paragraph(paragraph, doc_type)
                               })

                       structure_map["pages"].append(page_info)

                   except Exception as e:
                       # Fallback to OCR for scanned PDFs
                       content_blocks.extend(
                           await self._ocr_fallback(file_path, page_num)
                       )

           return {
               "content_blocks": content_blocks,
               "structure_map": structure_map,
               "total_pages": len(pdf_reader.pages),
               "metadata": self._extract_pdf_metadata(pdf_reader)
           }

       def _classify_paragraph(self, text: str, doc_type: str) -> str:
           """Classify paragraph type for legal documents"""
           text_lower = text.lower().strip()

           # Legal document patterns
           if any(keyword in text_lower for keyword in ['whereas', 'now therefore', 'in consideration of']):
               return 'preamble'
           elif text_lower.startswith(('section', 'article', 'clause')):
               return 'clause'
           elif any(keyword in text_lower for keyword in ['party agrees', 'shall', 'must', 'will']):
               return 'obligation'
           elif any(keyword in text_lower for keyword in ['signature', 'signed', 'executed']):
               return 'signature'
           elif len(text.split()) < 10:
               return 'heading'
           else:
               return 'paragraph'
   ```

3. **Legal-Aware Search Service**

   ```python
   # services/search_service.py
   from typing import List, Dict, Any, Optional
   from app.services.embedding_service import LegalEmbeddingService
   from app.services.supabase_client import SupabaseService

   class LegalSearchService:
       def __init__(self):
           self.embedding_service = LegalEmbeddingService()
           self.supabase_service = SupabaseService()

       async def search_clauses(
           self,
           query: str,
           document_types: Optional[List[str]] = None,
           clause_types: Optional[List[str]] = None,
           user_role: str = None,
           limit: int = 10
       ) -> List[Dict[str, Any]]:
           """Search for relevant clauses with legal context"""

           # Enhance query with legal context
           enhanced_query = await self._enhance_legal_query(query)

           # Generate embedding
           query_embedding = await self.embedding_service.get_embedding(enhanced_query)

           # Build search filters
           filters = self._build_legal_filters(document_types, clause_types, user_role)

           # Perform hybrid search (vector + filters)
           results = await self.supabase_service.legal_similarity_search(
               query_embedding=query_embedding,
               filters=filters,
               limit=limit
           )

           # Rerank results based on legal relevance
           reranked_results = await self._rerank_legal_results(query, results)

           return reranked_results

       async def _enhance_legal_query(self, query: str) -> str:
           """Enhance query with legal context and terminology"""

           # Legal term expansion
           legal_terms_map = {
               "termination": "termination, cancellation, dissolution, expiry",
               "liability": "liability, responsibility, damages, indemnification",
               "payment": "payment, compensation, remuneration, consideration",
               "confidentiality": "confidentiality, non-disclosure, proprietary information"
           }

           enhanced_query = query
           for term, expansion in legal_terms_map.items():
               if term.lower() in query.lower():
                   enhanced_query = enhanced_query.replace(term, expansion)

           return enhanced_query

       async def find_similar_clauses(
           self,
           example_clause: str,
           document_id: Optional[str] = None,
           similarity_threshold: float = 0.7
       ) -> List[Dict[str, Any]]:
           """Find clauses similar to a given example clause"""

           clause_embedding = await self.embedding_service.get_embedding(example_clause)

           filters = {}
           if document_id:
               filters["document_id"] = {"neq": document_id}  # Exclude same document

           results = await self.supabase_service.legal_similarity_search(
               query_embedding=clause_embedding,
               filters=filters,
               similarity_threshold=similarity_threshold,
               limit=20
           )

           return results
   ```

4. **AI Agent Framework for Legal Analysis**

   ```python
   # agents/compliance_agent.py
   from langchain.agents import initialize_agent, Tool
   from langchain.agents import AgentType
   from langchain_google_genai import ChatGoogleGenerativeAI
   from typing import List, Dict, Any

   class ComplianceAgent:
       def __init__(self):
           self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
           self.tools = self._initialize_tools()
           self.agent = initialize_agent(
               self.tools,
               self.llm,
               agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
               verbose=True
           )

       def _initialize_tools(self) -> List[Tool]:
           """Initialize legal analysis tools"""
           return [
               Tool(
                   name="search_legal_provisions",
                   description="Search for relevant legal provisions or regulations",
                   func=self._search_legal_provisions
               ),
               Tool(
                   name="analyze_clause_compliance",
                   description="Analyze if a clause complies with legal requirements",
                   func=self._analyze_clause_compliance
               ),
               Tool(
                   name="find_conflicting_clauses",
                   description="Find clauses that conflict with each other",
                   func=self._find_conflicting_clauses
               ),
               Tool(
                   name="generate_compliance_report",
                   description="Generate a comprehensive compliance report",
                   func=self._generate_compliance_report
               )
           ]

       async def check_document_compliance(
           self,
           document_id: str,
           jurisdiction: str = "US"
       ) -> Dict[str, Any]:
           """Check entire document for compliance issues"""

           prompt = f"""
           Analyze the legal document {document_id} for compliance issues in {jurisdiction} jurisdiction.

           Tasks:
           1. Search for relevant legal provisions that apply to this document type
           2. Analyze each major clause for compliance
           3. Identify any conflicting clauses within the document
           4. Generate a comprehensive compliance report with recommendations

           Provide detailed analysis with specific clause references and actionable recommendations.
           """

           result = await self.agent.arun(prompt)
           return self._parse_compliance_result(result)
   ```

5. **Clause Amendment Service**
   ```python
   # services/clause_service.py
   from typing import Dict, List, Any, Optional
   from app.services.supabase_client import SupabaseService
   from app.utils.position_mapper import PositionMapper

   class ClauseAmendmentService:
       def __init__(self):
           self.supabase_service = SupabaseService()
           self.position_mapper = PositionMapper()

       async def identify_clause_position(
           self,
           document_id: str,
           chunk_id: str
       ) -> Dict[str, Any]:
           """Get exact position of clause in original document"""

           chunk_data = await self.supabase_service.get_document_chunk(chunk_id)
           document_data = await self.supabase_service.get_document(document_id)

           position_info = chunk_data['position_info']

           return {
               "document_id": document_id,
               "chunk_id": chunk_id,
               "page_number": position_info['page'],
               "paragraph_index": position_info['paragraph_index'],
               "bounding_box": position_info.get('bounding_box'),
               "surrounding_context": await self._get_surrounding_context(chunk_id),
               "clause_content": chunk_data['chunk_content']
           }

       async def propose_amendment(
           self,
           chunk_id: str,
           original_text: str,
           proposed_text: str,
           reason: str,
           user_id: str
       ) -> Dict[str, Any]:
           """Propose an amendment to a clause"""

           # Validate the amendment
           validation_result = await self._validate_amendment(
               original_text, proposed_text, reason
           )

           if not validation_result['is_valid']:
               raise ValueError(validation_result['error'])

           # Store amendment proposal
           amendment_data = {
               'original_chunk_id': chunk_id,
               'original_text': original_text,
               'amended_text': proposed_text,
               'amendment_reason': reason,
               'amendment_type': validation_result['amendment_type'],
               'status': 'pending',
               'created_by': user_id
           }

           result = await self.supabase_service.supabase.table('clause_amendments').insert(
               amendment_data
           ).execute()

           return result.data[0]

       async def _validate_amendment(
           self,
           original: str,
           proposed: str,
           reason: str
       ) -> Dict[str, Any]:
           """Validate proposed amendment for legal consistency"""

           # Use AI to validate the amendment
           validation_prompt = f"""
           As a legal expert, validate this proposed clause amendment:

           Original: {original}
           Proposed: {proposed}
           Reason: {reason}

           Check for:
           1. Legal validity and consistency
           2. Potential conflicts with standard legal language
           3. Clarity and enforceability
           4. Amendment type (update/delete/add)

           Return: {{"is_valid": true/false, "error": "description", "amendment_type": "update/delete/add"}}
           """

           # Implementation would use Gemini for validation
           return {"is_valid": True, "amendment_type": "update"}
   ```
   **Frontend Structure (React TypeScript + Vite):**

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── documents/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── DocumentViewer.tsx      # PDF.js & DOCX viewer
│   │   │   ├── DocumentList.tsx
│   │   │   └── DocumentMetadata.tsx
│   │   ├── search/
│   │   │   ├── LegalSearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── ClauseHighlighter.tsx
│   │   │   └── SearchFilters.tsx
│   │   ├── clauses/
│   │   │   ├── ClauseEditor.tsx
│   │   │   ├── AmendmentWorkflow.tsx
│   │   │   ├── ClauseComparison.tsx
│   │   │   └── AmendmentHistory.tsx
│   │   ├── compliance/
│   │   │   ├── ComplianceChecker.tsx
│   │   │   ├── ComplianceReport.tsx
│   │   │   └── IssueTracker.tsx
│   │   ├── agents/
│   │   │   ├── AgentInterface.tsx
│   │   │   ├── QueryAgent.tsx
│   │   │   └── ComplianceAgent.tsx
│   │   ├── common/
│   │   │   ├── Layout.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── ConfirmDialog.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       └── Modal.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useDocuments.ts
│   │   ├── useLegalSearch.ts
│   │   ├── useClauses.ts
│   │   ├── useCompliance.ts
│   │   └── useAgents.ts
│   ├── services/
│   │   ├── api.ts              # Main API client
│   │   ├── auth.ts             # Authentication service
│   │   ├── documents.ts        # Document management
│   │   ├── search.ts           # Legal search service
│   │   ├── clauses.ts          # Clause management
│   │   ├── compliance.ts       # Compliance checking
│   │   ├── agents.ts           # AI agents service
│   │   └── supabase.ts         # Supabase client
│   ├── types/
│   │   ├── auth.ts             # Authentication types
│   │   ├── documents.ts        # Document types
│   │   ├── search.ts           # Search types
│   │   ├── clauses.ts          # Clause types
│   │   ├── compliance.ts       # Compliance types
│   │   ├── agents.ts           # Agent types
│   │   └── common.ts           # Common types
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   ├── legal-utils.ts      # Legal-specific utilities
│   │   └── document-viewer.ts  # Document viewing utilities
│   ├── styles/
│   │   ├── globals.css
│   │   ├── components.css
│   │   └── legal-theme.css     # Legal professional theme
│   ├── App.tsx                 # Main application
│   ├── main.tsx               # Entry point
│   └── vite-env.d.ts          # Vite type definitions
├── public/
│   ├── vite.svg
│   ├── favicon.ico
│   └── legal-icons/           # Legal-specific icons
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── vite.config.ts             # Vite configuration
└── tailwind.config.js         # Tailwind CSS config
```

**Frontend Implementation:**

1. **Document Viewer Component with Highlighting**

   ```typescript
   // components/documents/DocumentViewer.tsx
   import React, { useState, useEffect, useRef } from "react";
   import { Document, Page, pdfjs } from "react-pdf";
   import { HighlightArea } from "../types/documents";

   // Configure PDF.js worker
   pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

   interface DocumentViewerProps {
     documentId: string;
     fileUrl: string;
     highlights?: HighlightArea[];
     onClauseSelect?: (clauseId: string, position: any) => void;
   }

   const DocumentViewer: React.FC<DocumentViewerProps> = ({
     documentId,
     fileUrl,
     highlights = [],
     onClauseSelect,
   }) => {
     const [numPages, setNumPages] = useState<number>(0);
     const [currentPage, setCurrentPage] = useState<number>(1);
     const [scale, setScale] = useState<number>(1.0);
     const containerRef = useRef<HTMLDivElement>(null);

     const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
       setNumPages(numPages);
     };

     const renderHighlights = (pageNumber: number) => {
       return highlights
         .filter((h) => h.page === pageNumber)
         .map((highlight, index) => (
           <div
             key={index}
             className="absolute bg-yellow-200 bg-opacity-50 border border-yellow-400 cursor-pointer hover:bg-opacity-70"
             style={{
               left: `${highlight.x}%`,
               top: `${highlight.y}%`,
               width: `${highlight.width}%`,
               height: `${highlight.height}%`,
               transform: `scale(${scale})`,
             }}
             onClick={() => onClauseSelect?.(highlight.clauseId, highlight)}
             title={highlight.content?.substring(0, 100) + "..."}
           />
         ));
     };

     return (
       <div className="document-viewer h-full flex flex-col">
         {/* Toolbar */}
         <div className="flex items-center justify-between p-4 bg-gray-100 border-b">
           <div className="flex items-center space-x-4">
             <button
               onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
               disabled={currentPage <= 1}
               className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300"
             >
               Previous
             </button>
             <span className="text-sm">
               Page {currentPage} of {numPages}
             </span>
             <button
               onClick={() =>
                 setCurrentPage(Math.min(numPages, currentPage + 1))
               }
               disabled={currentPage >= numPages}
               className="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300"
             >
               Next
             </button>
           </div>

           <div className="flex items-center space-x-2">
             <button
               onClick={() => setScale(scale * 0.8)}
               className="px-2 py-1 bg-gray-500 text-white rounded"
             >
               Zoom Out
             </button>
             <span className="text-sm">{Math.round(scale * 100)}%</span>
             <button
               onClick={() => setScale(scale * 1.2)}
               className="px-2 py-1 bg-gray-500 text-white rounded"
             >
               Zoom In
             </button>
           </div>
         </div>

         {/* Document Display */}
         <div ref={containerRef} className="flex-1 overflow-auto p-4 relative">
           <Document
             file={fileUrl}
             onLoadSuccess={onDocumentLoadSuccess}
             loading={<div>Loading document...</div>}
             error={<div>Error loading document</div>}
           >
             <div className="relative">
               <Page
                 pageNumber={currentPage}
                 scale={scale}
                 loading={<div>Loading page...</div>}
               />
               {/* Overlay highlights */}
               <div className="absolute inset-0">
                 {renderHighlights(currentPage)}
               </div>
             </div>
           </Document>
         </div>
       </div>
     );
   };

   export default DocumentViewer;
   ```

2. **Legal Search Interface**

   ```typescript
   // components/search/LegalSearchBar.tsx
   import React, { useState, useCallback } from "react";
   import { Search, Filter, BookOpen } from "lucide-react";
   import { useLegalSearch } from "../../hooks/useLegalSearch";
   import { SearchFilters as ISearchFilters } from "../../types/search";

   interface LegalSearchBarProps {
     onResults: (results: any[]) => void;
     onLoading: (loading: boolean) => void;
   }

   const LegalSearchBar: React.FC<LegalSearchBarProps> = ({
     onResults,
     onLoading,
   }) => {
     const [query, setQuery] = useState("");
     const [showFilters, setShowFilters] = useState(false);
     const [filters, setFilters] = useState<ISearchFilters>({
       documentTypes: [],
       clauseTypes: [],
       dateRange: null,
       jurisdiction: "US",
     });

     const { searchClauses, searchSimilarClauses } = useLegalSearch();

     const handleSearch = useCallback(async () => {
       if (!query.trim()) return;

       onLoading(true);
       try {
         const results = await searchClauses(query, filters);
         onResults(results);
       } catch (error) {
         console.error("Search failed:", error);
         onResults([]);
       } finally {
         onLoading(false);
       }
     }, [query, filters, searchClauses, onResults, onLoading]);

     const handleSimilarSearch = useCallback(
       async (exampleClause: string) => {
         onLoading(true);
         try {
           const results = await searchSimilarClauses(exampleClause);
           onResults(results);
         } catch (error) {
           console.error("Similar search failed:", error);
           onResults([]);
         } finally {
           onLoading(false);
         }
       },
       [searchSimilarClauses, onResults, onLoading]
     );

     return (
       <div className="legal-search-bar space-y-4">
         {/* Main Search Input */}
         <div className="flex items-center space-x-2">
           <div className="flex-1 relative">
             <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
             <input
               type="text"
               value={query}
               onChange={(e) => setQuery(e.target.value)}
               onKeyPress={(e) => e.key === "Enter" && handleSearch()}
               placeholder="Search for clauses, legal terms, or ask questions..."
               className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
             />
           </div>

           <button
             onClick={handleSearch}
             className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
           >
             Search
           </button>

           <button
             onClick={() => setShowFilters(!showFilters)}
             className={`p-3 rounded-lg border transition-colors ${
               showFilters
                 ? "bg-blue-100 border-blue-300 text-blue-700"
                 : "bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200"
             }`}
           >
             <Filter className="w-5 h-5" />
           </button>
         </div>

         {/* Search Suggestions */}
         <div className="flex flex-wrap gap-2">
           {[
             "Termination clauses",
             "Liability limitations",
             "Payment terms",
             "Confidentiality agreements",
             "Force majeure provisions",
           ].map((suggestion) => (
             <button
               key={suggestion}
               onClick={() => {
                 setQuery(suggestion);
                 handleSearch();
               }}
               className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
             >
               {suggestion}
             </button>
           ))}
         </div>

         {/* Advanced Filters */}
         {showFilters && (
           <div className="p-4 bg-gray-50 rounded-lg border space-y-4">
             <h3 className="font-semibold text-gray-700">Search Filters</h3>

             <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
               {/* Document Types */}
               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Document Types
                 </label>
                 <select
                   multiple
                   value={filters.documentTypes}
                   onChange={(e) =>
                     setFilters({
                       ...filters,
                       documentTypes: Array.from(
                         e.target.selectedOptions,
                         (option) => option.value
                       ),
                     })
                   }
                   className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                 >
                   <option value="contract">Contracts</option>
                   <option value="policy">Policies</option>
                   <option value="law">Laws</option>
                   <option value="regulation">Regulations</option>
                 </select>
               </div>

               {/* Clause Types */}
               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Clause Types
                 </label>
                 <select
                   multiple
                   value={filters.clauseTypes}
                   onChange={(e) =>
                     setFilters({
                       ...filters,
                       clauseTypes: Array.from(
                         e.target.selectedOptions,
                         (option) => option.value
                       ),
                     })
                   }
                   className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                 >
                   <option value="termination">Termination</option>
                   <option value="liability">Liability</option>
                   <option value="payment">Payment</option>
                   <option value="confidentiality">Confidentiality</option>
                   <option value="force_majeure">Force Majeure</option>
                 </select>
               </div>

               {/* Jurisdiction */}
               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Jurisdiction
                 </label>
                 <select
                   value={filters.jurisdiction}
                   onChange={(e) =>
                     setFilters({
                       ...filters,
                       jurisdiction: e.target.value,
                     })
                   }
                   className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                 >
                   <option value="US">United States</option>
                   <option value="UK">United Kingdom</option>
                   <option value="EU">European Union</option>
                   <option value="CA">Canada</option>
                   <option value="AU">Australia</option>
                 </select>
               </div>
             </div>
           </div>
         )}
       </div>
     );
   };

   export default LegalSearchBar;
   ```

### 2. Contextual Memory Chatbots

#### Architecture Requirements

- **Framework**: FastAPI with WebSocket support for real-time chat
- **Memory Management**: Supabase for persistent conversation storage
- **Session Handling**: UUID-based session management in Supabase
- **LLM Integration**: Google Gemini with streaming support
- **Frontend**: React TypeScript with real-time updates

#### Implementation Guidelines

**Core Features:**

1. **Memory Management with Supabase**

   ```sql
   -- Conversations table
   CREATE TABLE conversations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES auth.users(id),
       title TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Messages table
   CREATE TABLE messages (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
       role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
       content TEXT NOT NULL,
       metadata JSONB DEFAULT '{}',
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

2. **FastAPI WebSocket Chat Implementation**

   ```python
   # routers/chat.py
   from fastapi import WebSocket, WebSocketDisconnect
   from app.services.chat_service import ChatService
   from app.services.supabase_client import SupabaseService
   import json

   @router.websocket("/ws/chat/{conversation_id}")
   async def websocket_chat(websocket: WebSocket, conversation_id: str):
       await websocket.accept()
       chat_service = ChatService()

       try:
           while True:
               # Receive message from client
               data = await websocket.receive_text()
               message_data = json.loads(data)

               # Process with chat service
               response = await chat_service.process_message(
                   conversation_id=conversation_id,
                   message=message_data['message'],
                   user_id=message_data['user_id']
               )

               # Send response back to client
               await websocket.send_text(json.dumps({
                   'type': 'response',
                   'data': response
               }))

       except WebSocketDisconnect:
           print(f"Client disconnected from conversation {conversation_id}")
   ```

3. **React Chat Interface**

   ```typescript
   // components/chat/ChatInterface.tsx
   import React, { useState, useEffect, useRef } from "react";
   import { useWebSocket } from "../hooks/useWebSocket";
   import { Message } from "../types/chat";

   const ChatInterface: React.FC = () => {
     const [messages, setMessages] = useState<Message[]>([]);
     const [inputValue, setInputValue] = useState("");
     const { sendMessage, lastMessage, connectionStatus } = useWebSocket();

     useEffect(() => {
       if (lastMessage) {
         const messageData = JSON.parse(lastMessage.data);
         if (messageData.type === "response") {
           setMessages((prev) => [...prev, messageData.data]);
         }
       }
     }, [lastMessage]);

     const handleSendMessage = () => {
       if (inputValue.trim()) {
         const userMessage: Message = {
           role: "user",
           content: inputValue,
           timestamp: new Date(),
         };

         setMessages((prev) => [...prev, userMessage]);
         sendMessage(JSON.stringify({ message: inputValue }));
         setInputValue("");
       }
     };

     return (
       <div className="chat-interface">
         <div className="messages">
           {messages.map((message, index) => (
             <div key={index} className={`message ${message.role}`}>
               {message.content}
             </div>
           ))}
         </div>
         <div className="input-area">
           <input
             value={inputValue}
             onChange={(e) => setInputValue(e.target.value)}
             onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
             placeholder="Type your message..."
           />
           <button onClick={handleSendMessage}>Send</button>
         </div>
       </div>
     );
   };
   ```

### 3. RAG Monitoring and Evaluation Systems

#### Architecture Requirements

- **Framework**: FastAPI with Supabase for data persistence
- **Dashboard**: React TypeScript with real-time updates
- **Evaluation**: LangSmith + RAGAS integration stored in Supabase
- **Monitoring**: Structured logging with Supabase Analytics
- **Reporting**: Automated report generation with export capabilities

#### Key Components

1. **Supabase Monitoring Schema**

   ```sql
   -- Query logs table
   CREATE TABLE query_logs (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES auth.users(id),
       query TEXT NOT NULL,
       response TEXT,
       response_time INTEGER, -- milliseconds
       retrieved_docs INTEGER,
       evaluation_scores JSONB,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Evaluation metrics table
   CREATE TABLE evaluation_metrics (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       query_log_id UUID REFERENCES query_logs(id),
       metric_name TEXT NOT NULL,
       metric_value FLOAT NOT NULL,
       metric_metadata JSONB,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Performance metrics table
   CREATE TABLE performance_metrics (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       endpoint TEXT NOT NULL,
       response_time INTEGER,
       status_code INTEGER,
       error_message TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

2. **Evaluation Service**

   ```python
   # services/evaluation_service.py
   from typing import Dict, List, Any
   from app.services.supabase_client import SupabaseService
   import asyncio

   class EvaluationService:
       def __init__(self):
           self.supabase_service = SupabaseService()

       async def evaluate_rag_response(
           self,
           query: str,
           response: str,
           context: List[str],
           query_log_id: str
       ) -> Dict[str, float]:
           """Evaluate RAG response using multiple metrics"""

           # Calculate metrics
           relevancy_score = await self._calculate_relevancy(query, response)
           faithfulness_score = await self._calculate_faithfulness(response, context)
           hallucination_score = await self._detect_hallucinations(response, context)

           metrics = {
               "relevancy": relevancy_score,
               "faithfulness": faithfulness_score,
               "hallucination_score": hallucination_score
           }

           # Store metrics in Supabase
           await self._store_evaluation_metrics(query_log_id, metrics)

           return metrics

       async def _store_evaluation_metrics(
           self,
           query_log_id: str,
           metrics: Dict[str, float]
       ):
           """Store evaluation metrics in Supabase"""
           for metric_name, metric_value in metrics.items():
               await self.supabase_service.supabase.table('evaluation_metrics').insert({
                   'query_log_id': query_log_id,
                   'metric_name': metric_name,
                   'metric_value': metric_value
               }).execute()
   ```

3. **Real-time Dashboard Component**

   ```typescript
   // components/dashboard/MetricsDashboard.tsx
   import React, { useState, useEffect } from "react";
   import { supabase } from "../../services/supabase";
   import { RealtimeChannel } from "@supabase/supabase-js";

   interface Metric {
     id: string;
     metric_name: string;
     metric_value: number;
     created_at: string;
   }

   const MetricsDashboard: React.FC = () => {
     const [metrics, setMetrics] = useState<Metric[]>([]);
     const [loading, setLoading] = useState(true);

     useEffect(() => {
       // Fetch initial metrics
       fetchMetrics();

       // Set up real-time subscription
       const channel: RealtimeChannel = supabase
         .channel("evaluation_metrics")
         .on(
           "postgres_changes",
           { event: "INSERT", schema: "public", table: "evaluation_metrics" },
           (payload) => {
             setMetrics((prev) => [...prev, payload.new as Metric]);
           }
         )
         .subscribe();

       return () => {
         supabase.removeChannel(channel);
       };
     }, []);

     const fetchMetrics = async () => {
       const { data, error } = await supabase
         .from("evaluation_metrics")
         .select("*")
         .order("created_at", { ascending: false })
         .limit(100);

       if (!error && data) {
         setMetrics(data);
       }
       setLoading(false);
     };

     return (
       <div className="metrics-dashboard">
         <h2>Real-time Evaluation Metrics</h2>
         {loading ? (
           <div>Loading metrics...</div>
         ) : (
           <div className="metrics-grid">
             {metrics.map((metric) => (
               <div key={metric.id} className="metric-card">
                 <h3>{metric.metric_name}</h3>
                 <p className="metric-value">
                   {metric.metric_value.toFixed(3)}
                 </p>
                 <p className="metric-time">
                   {new Date(metric.created_at).toLocaleString()}
                 </p>
               </div>
             ))}
           </div>
         )}
       </div>
     );
   };
   ```

## General Implementation Standards

### Code Quality Requirements

1. **Python Projects**

   - Follow PEP 8 standards
   - Use type hints for all functions
   - Implement comprehensive error handling
   - Include docstrings with parameter descriptions
   - Use Pydantic models for data validation

2. **Java Projects**

   - Follow Spring Boot best practices
   - Use proper dependency injection
   - Implement comprehensive exception handling
   - Include Javadoc documentation
   - Use appropriate design patterns

3. **Frontend Projects**
   - Use modern React patterns (hooks, functional components)
   - Implement proper error boundaries
   - Use TypeScript where applicable
   - Follow responsive design principles
   - Implement proper state management

### Security Requirements

1. **Authentication & Authorization**

   - Server-side token validation
   - Role-based access control
   - Secure API endpoints
   - Input validation and sanitization

2. **Data Protection**
   - Environment variable management
   - API key protection
   - Secure communication (HTTPS)
   - Audit logging for sensitive operations

### Performance Requirements

1. **API Performance**

   - p95 latency < 3 seconds
   - Efficient database queries
   - Proper caching strategies
   - Connection pooling

2. **Frontend Performance**
   - Lazy loading for large datasets
   - Optimized bundle sizes
   - Proper state management
   - Loading states for user feedback

### Testing Requirements

1. **Backend Testing**

   - Unit tests for all services
   - Integration tests for API endpoints
   - Mock external dependencies
   - Test error conditions and edge cases

2. **Frontend Testing**
   - Component testing with React Testing Library
   - End-to-end testing with Cypress or Playwright
   - Accessibility testing
   - Cross-browser compatibility

### Configuration Management

1. **Environment Variables**

   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

   # Google Gemini API
   GOOGLE_API_KEY=your_gemini_api_key

   # FastAPI Configuration
   SECRET_KEY=your_jwt_secret_key
   CORS_ORIGINS=["http://localhost:5173", "https://your-domain.com"]

   # LangSmith (for monitoring)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=your_project_name

   # Application Settings
   LOG_LEVEL=INFO
   DEBUG=false
   ```

2. **Frontend Environment Variables**

   ```bash
   # Frontend (.env)
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Supabase Configuration**
   ```typescript
   // config/supabase.ts
   export interface Database {
     public: {
       Tables: {
         documents: {
           Row: {
             id: string;
             content: string;
             embedding: number[];
             metadata: Record<string, any>;
             role: "hr" | "engineering" | "public";
             created_at: string;
             updated_at: string;
           };
           Insert: Omit<
             Database["public"]["Tables"]["documents"]["Row"],
             "id" | "created_at" | "updated_at"
           >;
           Update: Partial<Database["public"]["Tables"]["documents"]["Insert"]>;
         };
         query_logs: {
           Row: {
             id: string;
             user_id: string;
             query: string;
             response: string | null;
             response_time: number | null;
             retrieved_docs: number | null;
             evaluation_scores: Record<string, any> | null;
             created_at: string;
           };
         };
       };
       Functions: {
         match_documents: {
           Args: {
             query_embedding: number[];
             user_role: string;
             match_threshold: number;
             match_count: number;
           };
           Returns: Array<{
             id: string;
             content: string;
             metadata: Record<string, any>;
             similarity: number;
           }>;
         };
       };
     };
   }
   ```

## Project Structure Templates

### FastAPI + Supabase + React TypeScript Project

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Auth models
│   │   │   ├── documents.py     # Document models
│   │   │   └── rag.py           # RAG models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── rag.py           # RAG endpoints
│   │   │   └── chat.py          # Chat endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── supabase_client.py
│   │   │   ├── auth_service.py
│   │   │   ├── rag_service.py
│   │   │   └── evaluation_service.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   ├── config.py
│   │   └── database.py
│   ├── migrations/              # Supabase migrations
│   │   └── 001_initial_schema.sql
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_rag.py
│   │   └── test_evaluation.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   ├── chat/
│   │   │   ├── dashboard/
│   │   │   └── common/
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useRAG.ts
│   │   │   └── useSupabase.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── supabase.ts
│   │   │   └── auth.ts
│   │   ├── types/
│   │   │   ├── database.ts
│   │   │   ├── auth.ts
│   │   │   └── rag.ts
│   │   ├── utils/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   │   └── 20240101000000_initial_schema.sql
│   └── functions/
│       ├── match-documents/
│       └── rag-query/
├── docker-compose.yml
├── .gitignore
└── README.md
```

### Required Dependencies

**Backend (requirements.txt):**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.2
pydantic==2.5.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
google-generativeai==0.3.2
langchain==0.1.0
langchain-google-genai==0.0.6
numpy==1.24.3
pytest==7.4.3
httpx==0.25.2
websockets==12.0
asyncpg==0.29.0
```

**Frontend (package.json):**

```json
{
  "name": "rag-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "@supabase/supabase-js": "^2.38.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.294.0",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.1.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "vitest": "^1.0.0"
  }
}
```

## Deployment Instructions

### Supabase Setup

1. **Create Supabase Project**

   - Go to https://supabase.com/dashboard
   - Create new project
   - Note the project URL and anon key

2. **Enable pgvector Extension**

   ```sql
   -- Run in Supabase SQL editor
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Set up Database Schema**

   ```sql
   -- Run migration scripts
   -- Create tables, indexes, and RLS policies
   ```

4. **Configure Authentication**
   - Enable email/password authentication
   - Set up custom user metadata for roles
   - Configure email templates

### Docker Deployment

1. **Backend Dockerfile**

   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Frontend Dockerfile**

   ```dockerfile
   FROM node:18-alpine as build

   WORKDIR /app
   COPY package*.json ./
   RUN npm ci

   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=build /app/dist /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/nginx.conf

   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

3. **Docker Compose**

   ```yaml
   version: "3.8"
   services:
     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         - SUPABASE_URL=${SUPABASE_URL}
         - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
         - GOOGLE_API_KEY=${GOOGLE_API_KEY}
       depends_on:
         - redis

     frontend:
       build: ./frontend
       ports:
         - "80:80"
       depends_on:
         - backend

     redis:
       image: redis:alpine
       ports:
         - "6379:6379"
   ```

### Cloud Deployment (Vercel + Railway)

1. **Frontend on Vercel**

   - Connect GitHub repository
   - Set environment variables
   - Deploy with automatic CI/CD

2. **Backend on Railway**
   - Connect GitHub repository
   - Configure environment variables
   - Set up automatic deployments

### Production Checklist

- [ ] Environment variables configured
- [ ] Supabase RLS policies enabled
- [ ] CORS origins restricted
- [ ] API rate limiting implemented
- [ ] Monitoring and logging configured
- [ ] SSL certificates installed
- [ ] Database backups scheduled

## Documentation Requirements

1. **README.md Structure**

   - Project overview and features
   - Installation and setup instructions
   - Configuration details
   - Usage examples
   - API documentation
   - Contributing guidelines

2. **API Documentation**

   - OpenAPI/Swagger specifications
   - Request/response examples
   - Authentication requirements
   - Error code explanations

3. **User Documentation**
   - User guides for each feature
   - FAQ sections
   - Troubleshooting guides
   - Video tutorials (if applicable)

## Success Metrics

### Data Segregation (for RAG systems)

- 100% pass rate on role-based access tests
- Cross-role isolation verification
- No unauthorized document access

### Performance Metrics

- API response time < 3 seconds (p95)
- UI responsiveness < 100ms for interactions
- Memory usage optimization
- Scalability under load

### User Experience Metrics

- Intuitive interface design
- Clear error messages
- Proper loading states
- Mobile responsiveness
- Accessibility compliance

## Troubleshooting Guide

### Common Issues

1. **Supabase Connection Errors**

   - Verify SUPABASE_URL and SUPABASE_ANON_KEY
   - Check if pgvector extension is enabled
   - Ensure RLS policies are correctly configured

2. **Authentication Problems**

   - Verify JWT configuration in Supabase
   - Check user metadata schema
   - Ensure proper CORS configuration

3. **Vector Search Issues**

   - Verify embeddings are properly stored
   - Check vector similarity function
   - Ensure proper indexing on vector column

4. **Frontend Build Errors**

   - Check TypeScript configuration
   - Verify all dependencies are installed
   - Ensure environment variables are set

5. **Real-time Issues**
   - Check Supabase real-time configuration
   - Verify WebSocket connections
   - Ensure proper channel subscriptions

### Debugging Steps

1. **Backend Debugging**

   ```bash
   # Enable debug logging
   export LOG_LEVEL=DEBUG

   # Check Supabase connection
   python -c "from app.services.supabase_client import SupabaseService; print('Connected:', SupabaseService().supabase.table('documents').select('id').limit(1).execute())"

   # Test API endpoints
   curl -X GET "http://localhost:8000/api/health"
   ```

2. **Frontend Debugging**

   ```bash
   # Check build
   npm run build

   # Run in development mode
   npm run dev

   # Check TypeScript errors
   npx tsc --noEmit
   ```

3. **Database Debugging**

   ```sql
   -- Check vector extension
   SELECT * FROM pg_extension WHERE extname = 'vector';

   -- Check document count
   SELECT COUNT(*) FROM documents;

   -- Test vector similarity
   SELECT content, embedding <-> '[1,2,3,...]' AS distance
   FROM documents
   ORDER BY distance
   LIMIT 5;
   ```

### Performance Optimization

1. **Database Optimization**

   - Create proper indexes on frequently queried columns
   - Use connection pooling
   - Implement query caching
   - Monitor slow queries

2. **API Optimization**

   - Implement response caching
   - Use async/await properly
   - Optimize embedding generation
   - Implement request rate limiting

3. **Frontend Optimization**
   - Use React.memo for expensive components
   - Implement proper loading states
   - Use virtual scrolling for large lists
   - Optimize bundle size with code splitting

This comprehensive guide provides detailed instructions for implementing GenAI applications using the **Python (FastAPI) + Supabase + React TypeScript** tech stack. The instructions cover complete project structure, implementation patterns, deployment strategies, and troubleshooting guidelines specifically tailored to this modern stack combination.
