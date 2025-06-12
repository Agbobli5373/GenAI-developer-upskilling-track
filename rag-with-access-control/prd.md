# Product Requirements Document: RAG with Document-Level Access Control

**Document Status:** Draft
**Author:** [Your Name]
**Stakeholders:** [Your Name, Project Lead, etc.]
**Last Updated:** [Date]

## 1. Introduction & Problem Statement

### 1.1. Background
Our current Retrieval-Augmented Generation (RAG) system is highly effective at retrieving relevant information from our entire knowledge base to answer user queries. However, it operates on a "single pool" of data, meaning any user can potentially access any document in the vector store.

### 1.2. Problem Statement
As we ingest more sensitive and role-specific documents (e.g., financial reports, HR policies, engineering roadmaps), the lack of access control presents a critical security and compliance risk. A user asking a general question could inadvertently be shown confidential information they are not authorized to see, leading to data leakage. We need a mechanism to ensure the RAG system respects data boundaries and only shows users information pertinent to their role.

## 2. Goals & Objectives

### 2.1. Primary Goal
To enhance our RAG system with a robust, document-level access control mechanism that prevents unauthorized users from accessing sensitive or role-restricted information.

### 2.2. Key Objectives

*   **Security:** Implement a "filter-first" retrieval strategy where data is filtered by access rights before being sent to the LLM.
*   **Scalability:** The access control model should be easily extensible to support new roles and permissions in the future without a major architectural redesign.
*   **User Experience:** The access control layer should be transparent to the end-user and not significantly degrade the performance or relevance of the RAG system's answers.
*   **Deliverable:** Produce a working RAG application that demonstrates role-based filtering successfully.

## 3. User Personas & Stories

We will focus on three primary user roles for this project:

| Persona | Role | Needs & Goals |
| :--- | :--- | :--- |
| Helen | HR Manager | Needs to query confidential HR documents (performance reviews, salary bands) and general company information. |
| Evan | Software Engineer | Needs to query technical documentation (sprint plans, architecture diagrams) and general company information. |
| Pat | Public User/Guest | Can only access publicly available information (company mission, public blog posts). |

**User Stories:**

*   As Helen (HR Manager), I want to ask questions about performance review guidelines, so that I can get quick answers without seeing irrelevant engineering documents.
*   As Evan (Engineer), I want to ask about our CI/CD pipeline, so that I get a technical answer and am not shown confidential HR files.
*   As Pat (Public User), when I ask about company policies, I want to see only the public information, so that I am not exposed to sensitive internal data.
*   As an Admin, I want to tag new documents with role metadata (hr, engineering, public), so that the system can enforce the correct access policies during retrieval.

## 4. Feature Requirements

This section details the specific features to be built.

**FR-1: Document Metadata Tagging**

*   **Description:** The data ingestion process must be updated to associate each document (or document chunk) with access control metadata.
*   **Acceptance Criteria:**
    *   The documents table in Supabase (or collection in ChromaDB) must have a metadata field.
    *   This metadata field will store a JSON object, e.g., `{ "role": "hr" }`.
    *   The ingestion script must successfully write both the content embedding and the role metadata for each document.

**FR-2: Role-Based Retrieval Filtering**

*   **Description:** The core retrieval logic must be modified to use the user's role to filter documents before performing the similarity search.
*   **Acceptance Criteria:**
    *   The retrieval query must filter for documents where the `metadata.role` matches the user's role OR the `metadata.role` is "public".
    *   This logic should be implemented securely on the backend (e.g., in a Supabase RPC function or via LangChain's retriever filter) to prevent client-side manipulation.
    *   If a user's query matches a document they don't have access to, that document must NOT be included in the context for the LLM.

**FR-3: Mock User Authentication Stub**

*   **Description:** A simple mechanism to simulate user login and obtain an identity token containing their role. This is a stub and not a full-featured authentication system.
*   **Acceptance Criteria:**
    *   An API endpoint (e.g., `/api/auth/login`) will accept a role (e.g., "hr") as input.
    *   The endpoint will return a JWT (JSON Web Token) containing the role in its payload (e.g., `{ "role": "hr", "exp": ... }`).
    *   The JWT should be signed with a secret key.

**FR-4: Secure RAG API Endpoint**

*   **Description:** The primary RAG API endpoint that receives user queries must be protected and role-aware.
*   **Acceptance Criteria:**
    *   The endpoint must require a valid JWT in the `Authorization` header.
    *   It must validate the token and extract the user's role from the payload.
    *   It must pass this role to the retrieval logic (FR-2) to fetch filtered results.
    *   It sends the filtered context and query to the Gemini LLM for final answer generation.

## 5. Non-Functional Requirements (NFRs)

*   **NFR-1: Security:** The system must adhere to a "zero-trust" principle. Filtering must happen on the server-side and should not be bypassable by the client.
*   **NFR-2: Performance:** The addition of metadata filtering should not add more than 20% latency to the overall p95 response time of the retrieval step.

## 6. Out of Scope

To ensure delivery within the 1-week timeframe, the following are explicitly out of scope:

*   A full user interface for logging in (a simple dropdown and button is sufficient).
*   A user management system (creating/deleting users, assigning roles).
*   Complex, multi-level permission models (e.g., user-level permissions, group memberships).
*   A UI for tagging documents (this will be handled by the ingestion script).

## 7. Success Metrics

How we will measure the success of this project:

| Metric | Measurement | Target |
| :--- | :--- | :--- |
| Data Segregation | Pass/Fail on a series of structured tests. | 100% Pass Rate. An "engineering" user must never see content from an "hr" document. |
| API Response Time | The end-to-end latency of a query to the `/api/rag` endpoint. | p95 latency should remain under 3 seconds. |
| Functionality | Completion of all feature requirements. | All acceptance criteria for FR-1 through FR-4 are met. |

## 8. Milestone Plan (for a 1-week project)

**Day 1-2: Foundation & Data.**

*   **Task:** Set up project structure (FastAPI/Next.js).
*   **Task:** Update database schema to include metadata field.
*   **Task:** Write and run the `ingest.py` script to populate the vector store with tagged documents.

**Day 3: Core Logic.**

*   **Task:** Build the mock authentication endpoint (`/api/auth/login`).
*   **Task:** Implement the filtered retrieval logic (Supabase function or LangChain retriever).

**Day 4: API Integration.**

*   **Task:** Develop the secure, role-aware RAG API endpoint (`/api/rag`).
*   **Task:** Unit test the endpoint with different roles.

**Day 5: Frontend & E2E Testing.**

*   **Task:** Build the simple Vite/Next.js frontend to interact with the API.
*   **Task:** Perform end-to-end testing based on the user stories to validate success metrics.
*   **Task:** Finalize documentation.