# Copilot Agent Instructions for GenAI Application Implementation

## Overview

This document provides comprehensive instructions for a Copilot agent to implement various types of GenAI applications based on established patterns and requirements found in the workspace projects.

## Core Application Types

### 1. RAG (Retrieval-Augmented Generation) Systems

#### Architecture Requirements

- **Backend**: FastAPI or Spring Boot for API endpoints
- **Frontend**: React/Vite or Next.js for modern UI
- **Vector Database**: ChromaDB or Supabase for document storage
- **LLM Integration**: Google Gemini or OpenAI for response generation
- **Authentication**: JWT-based role management

#### Implementation Guidelines

**Backend Structure:**

```
backend/
├── main.py              # FastAPI application entry
├── ingest.py           # Document ingestion pipeline
├── models/             # Pydantic data models
├── services/           # Business logic services
├── auth/               # Authentication handlers
├── config/             # Configuration management
└── requirements.txt    # Dependencies
```

**Key Components to Implement:**

1. **Document Ingestion Service**

   - Process PDF, TXT, ODT documents
   - Generate embeddings using sentence-transformers
   - Store with role-based metadata: `{"role": "hr|engineering|public"}`
   - Implement chunking strategy (500-1000 tokens per chunk)

2. **Authentication Service**

   - Mock authentication endpoint: `/api/auth/login`
   - JWT token generation with role payload
   - Token validation middleware
   - Role-based access control

3. **RAG Query Service**

   - Secure endpoint: `/api/rag`
   - Role-based document filtering before retrieval
   - Similarity search with metadata filtering
   - LLM response generation with context

4. **Access Control Implementation**
   ```python
   # Example filtering logic
   def filter_documents_by_role(user_role: str, query_vector):
       filters = {"role": {"$in": [user_role, "public"]}}
       return vector_store.similarity_search(
           query_vector,
           filter=filters,
           k=5
       )
   ```

**Frontend Structure:**

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── services/       # API integration
│   ├── hooks/         # Custom React hooks
│   ├── styles/        # CSS/styling
│   └── App.jsx        # Main application
├── public/            # Static assets
├── package.json       # Dependencies
└── vite.config.js     # Build configuration
```

**UI Requirements:**

- Role selection interface (HR, Engineering, Public)
- Query input with sample questions per role
- Response display with source citations
- Loading states and error handling
- Mobile-responsive design
- Modern gradient backgrounds and card layouts

### 2. Contextual Memory Chatbots

#### Architecture Requirements

- **Framework**: Spring Boot with Thymeleaf or Streamlit
- **Memory Management**: LangChain ConversationBufferMemory
- **Session Handling**: UUID-based session management
- **LLM Integration**: Google Gemini with streaming support

#### Implementation Guidelines

**Core Features:**

1. **Memory Management**

   - Session-based conversation history
   - Configurable memory window (default: 10 exchanges)
   - Memory trimming to prevent token overflow
   - Session isolation for multiple conversations

2. **Chat Interface**

   - Real-time message display
   - Typing indicators
   - Message timestamps
   - Session controls (clear, new session)
   - Memory viewer for debugging

3. **Spring Boot Implementation**

   ```java
   @RestController
   public class ChatController {
       @PostMapping("/api/chat")
       public ResponseEntity<ChatResponse> chat(
           @RequestBody ChatRequest request,
           @RequestHeader("Session-ID") String sessionId
       ) {
           // Implement chat logic with memory
       }
   }
   ```

4. **Settings and Configuration**
   - Dark/light mode toggle
   - Font size adjustment
   - Animation controls
   - Context length settings
   - Performance mode options

### 3. RAG Monitoring and Evaluation Systems

#### Architecture Requirements

- **Framework**: Python with Streamlit dashboard
- **Evaluation**: LangSmith + RAGAS integration
- **Monitoring**: Structured logging with JSON format
- **Reporting**: Automated report generation

#### Key Components

1. **Evaluation Framework**

   ```python
   class RAGEvaluator:
       def __init__(self):
           self.langsmith_client = LangSmithClient()
           self.ragas_evaluator = RAGASEvaluator()

       def evaluate_query(self, query, response, context):
           metrics = {
               "relevancy": self.calculate_relevancy(query, response),
               "faithfulness": self.calculate_faithfulness(response, context),
               "hallucination_score": self.detect_hallucinations(response, context)
           }
           return metrics
   ```

2. **Monitoring System**

   - Query logging with structured format
   - Performance metrics (latency, throughput)
   - Real-time alerts for performance degradation
   - Document retrieval analytics

3. **Interactive Dashboard**
   - Performance overview with KPI visualization
   - Query analysis and trend tracking
   - Quality metrics display
   - Export capabilities (PDF, CSV, JSON)

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
   # API Configuration
   GOOGLE_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_key

   # Database Configuration
   DATABASE_URL=your_database_url
   VECTOR_DB_PATH=./data/chroma_db

   # Authentication
   JWT_SECRET_KEY=your_jwt_secret
   JWT_EXPIRY_HOURS=24

   # Monitoring
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LOG_LEVEL=INFO
   ```

2. **Configuration Files**
   - Separate configs for development/production
   - Centralized configuration management
   - Validation of required settings
   - Default value handling

## Project Structure Templates

### Python FastAPI RAG Project

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   ├── auth/
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── documents/
├── docker-compose.yml
└── README.md
```

### Spring Boot Chatbot Project

```
project/
├── src/
│   ├── main/
│   │   ├── java/com/company/chatbot/
│   │   │   ├── controller/
│   │   │   ├── service/
│   │   │   ├── model/
│   │   │   ├── config/
│   │   │   └── Application.java
│   │   └── resources/
│   │       ├── templates/
│   │       ├── static/
│   │       └── application.yml
│   └── test/
├── pom.xml
└── README.md
```

## Deployment Instructions

### Docker Deployment

1. Create Dockerfile for each service
2. Use docker-compose for multi-service setup
3. Include environment variable configuration
4. Set up proper networking and volumes

### Cloud Deployment

1. Configure cloud provider (AWS, GCP, Azure)
2. Set up CI/CD pipelines
3. Configure monitoring and logging
4. Implement proper scaling strategies

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

1. **API Key Errors**: Verify environment variables
2. **Database Connection**: Check connection strings and credentials
3. **CORS Issues**: Configure proper CORS settings
4. **Memory Issues**: Implement proper memory management
5. **Authentication Problems**: Verify JWT configuration

### Debugging Steps

1. Check application logs
2. Verify configuration settings
3. Test API endpoints individually
4. Use browser developer tools
5. Check network connectivity

This comprehensive guide should enable a Copilot agent to implement robust GenAI applications following established patterns and best practices found in your workspace projects.
