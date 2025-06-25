from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.api_v1.endpoints.auth import verify_token
from app.core.database import supabase
from app.models.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(current_user_id: str = Depends(verify_token)):
    """Get all users (admin only)"""
    try:
        # Check if current user is admin
        current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
        if not current_user.data or current_user.data[0]["role"] != "Legal Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        result = supabase.table("users").select("*").execute()
        return [UserResponse(**user) for user in result.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user_id: str = Depends(verify_token)):
    """Get user by ID"""
    try:
        # Users can only access their own profile or admins can access any
        current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
        if current_user_id != user_id and (not current_user.data or current_user.data[0]["role"] != "Legal Admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
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


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user_id: str = Depends(verify_token)):
    """Update user"""
    try:
        # Users can only update their own profile or admins can update any
        current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
        if current_user_id != user_id and (not current_user.data or current_user.data[0]["role"] != "Legal Admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update user
        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            result = supabase.table("users").update(update_data).eq("id", user_id).execute()
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return UserResponse(**result.data[0])
        
        # If no updates, return current user
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return UserResponse(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user_id: str = Depends(verify_token)):
    """Delete user (admin only)"""
    try:
        # Check if current user is admin
        current_user = supabase.table("users").select("role").eq("id", current_user_id).execute()
        if not current_user.data or current_user.data[0]["role"] != "Legal Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Soft delete user
        result = supabase.table("users").update({"is_active": False}).eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
