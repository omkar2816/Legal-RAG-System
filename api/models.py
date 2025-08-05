"""Models for the Legal RAG System"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str

class UserInDB(UserBase):
    """User model as stored in the database"""
    hashed_password: str

class User(UserBase):
    """User model returned to clients"""
    id: str

class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None

class AnswerResponse(BaseModel):
    """Model for formatted answers response"""
    answers: List[str]

class DocumentQuestionRequest(BaseModel):
    """Model for document URL and questions request used by the HackRx Run API"""
    documents: str = Field(..., description="URL of the document to process")
    questions: List[str] = Field(..., description="List of questions to ask about the document")