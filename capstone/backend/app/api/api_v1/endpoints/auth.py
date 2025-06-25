from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import supabase, supabase_admin
from app.models.user import UserCreate, UserResponse, UserLogin

router = APIRouter()
security = HTTPBearer()


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    try:
        # Create user in Supabase Auth with email confirmation disabled for development
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.full_name,
                    "role": user.role.value  # Use .value to get the string value of the enum
                },
                "email_redirect_to": None  # Disable email confirmation redirect
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        # Wait a moment for the trigger to execute
        import time
        time.sleep(1.0)  # Increased wait time
        
        # Check if user record was created by trigger using admin client to bypass RLS
        result = supabase_admin.table("users").select("*").eq("id", auth_response.user.id).execute()
        
        # Automatically confirm the user's email for development purposes
        try:
            # Execute SQL to confirm the user's email
            supabase_admin.rpc("exec_sql", {
                "query": f"UPDATE auth.users SET email_confirmed_at = now(), confirmation_token = '' WHERE id = '{auth_response.user.id}'"
            }).execute()
        except Exception as e:
            # If auto-confirmation fails, continue anyway - user can confirm manually
            print(f"Failed to auto-confirm user email: {e}")
        
        if not result.data:
            # Trigger didn't work, create the user record manually using admin client
            # This bypasses RLS policies since we're using the service role key
            user_data = {
                "id": auth_response.user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": True,
            }
            
            try:
                # Use admin client to bypass RLS and create user record
                result = supabase_admin.table("users").insert(user_data).execute()
                    
                if not result.data:
                    raise Exception("Failed to create user record after multiple attempts")
                    
            except Exception as db_error:
                raise Exception(f"Database error saving new user: {str(db_error)}")
        
        return UserResponse(**result.data[0])
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user and return access token"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": auth_response.user.id, "email": auth_response.user.email},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_access_token(
            data={"sub": auth_response.user.id, "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/logout")
async def logout(user_id: str = Depends(verify_token)):
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(verify_token)):
    """Get current user information"""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**result.data[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )
