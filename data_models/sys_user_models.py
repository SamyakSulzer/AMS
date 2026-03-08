from pydantic import BaseModel, Field
from typing import Optional, Literal

class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    user_emp_id: int
    user_emp_name: str = Field(..., max_length=50)
    user_role: Literal["administrator", "viewer", "master manager"]

class UserCreate(UserBase):
    password: str = Field(..., alias="pass", max_length=50)

class UserLogin(BaseModel):
    username: str
    password: str = Field(..., alias="pass")

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
