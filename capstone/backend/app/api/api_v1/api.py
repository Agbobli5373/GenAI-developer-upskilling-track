from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, documents, users, search, enhanced_search

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(enhanced_search.router, prefix="/enhanced-search", tags=["enhanced-search"])
