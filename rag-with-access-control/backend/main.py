from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

# --- 1. Initialize FastAPI and Security ---
app = FastAPI(title="RAG with Access Control API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- 2. Load Vector Store and Embeddings ---
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = Chroma(
    collection_name="rag-chroma",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# --- 3. Define RAG Chain ---
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

prompt_template = """
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}
Context: {context}

Answer:
"""
prompt = PromptTemplate.from_template(prompt_template)

def get_retriever(role: str):
    return vector_store.as_retriever(
        search_kwargs={"filter": {"role": {"$in": [role, "public"]}}}
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- 4. Define API Models ---
class QueryRequest(BaseModel):
    question: str

class TokenData(BaseModel):
    role: str | None = None

# --- 5. Define Authentication Logic ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")  # Use env var in production
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(role=role)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- 6. Define API Endpoints ---
class LoginRequest(BaseModel):
    role: str

@app.post("/api/auth/login")
def login(request: LoginRequest):
    """Mock authentication endpoint that returns a JWT token with the user's role."""
    # Validate that the role is one of the expected roles
    valid_roles = ["hr", "engineering", "public"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    # In a real app, you would validate the user's credentials here
    # For this mock service, we'll just create a token with the provided role
    to_encode = {"role": request.role}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@app.post("/api/rag")
def rag_query(
    request: QueryRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Secure, role-aware RAG API endpoint that filters documents by user role."""
    try:
        # Get role-filtered retriever
        role = current_user.role if current_user.role is not None else "public"
        retriever = get_retriever(role)
        
        # Build and execute RAG chain
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Execute the chain and get the answer
        answer = rag_chain.invoke(request.question)
        
        return {
            "answer": answer,
            "user_role": current_user.role,
            "question": request.question
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "RAG API is running"}

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG with Access Control API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "login": "/api/auth/login",
            "rag": "/api/rag"
        }
    }