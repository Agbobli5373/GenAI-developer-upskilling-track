import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define Documents and Metadata ---
# In a real-world scenario, this would come from a database or file system.
documents = [
    "HR Policy: All employees are entitled to 25 days of paid vacation per year.",
    "HR Policy: Performance reviews are conducted annually in December.",
    "Engineering Guideline: All new code must be submitted via a pull request.",
    "Engineering Guideline: System architecture diagrams are stored in Confluence.",
    "Public Announcement: Our company is proud to announce a new partnership with Acme Corp.",
    "Public Announcement: We will be hosting a public webinar on the future of AI next month."
]

metadatas = [
    {"role": "hr"},
    {"role": "hr"},
    {"role": "engineering"},
    {"role": "engineering"},
    {"role": "public"},
    {"role": "public"}
]

# --- 2. Initialize Embeddings and Vector Store ---
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = Chroma(
    collection_name="rag-chroma",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# --- 3. Add Documents to the Vector Store ---
vector_store.add_texts(
    texts=documents,
    metadatas=metadatas
)

print("Data ingestion complete.")