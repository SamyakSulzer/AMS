from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.dependencies import get_db
from database.repositories.sys_user_repository import UserRepository
from data_models.sys_user_models import UserCreate, UserLogin, UserResponse
from typing import List

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    existing_user = await repo.get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    user = await repo.create_user(
        username=user_in.username,
        password=user_in.password,
        user_emp_id=user_in.user_emp_id,
        user_emp_name=user_in.user_emp_name,
        user_role=user_in.user_role
    )
    return user

@router.post("/login")
async def login_user(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    user = await repo.get_user_by_username(user_in.username)
    
    # Matching simple plain text as requested by "removing all security measure"
    if not user or user.pass_ != user_in.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "role": user.user_role,
        "emp_name": user.user_emp_name
    }

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    return await repo.get_all_users()
