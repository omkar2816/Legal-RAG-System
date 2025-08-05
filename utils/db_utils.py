"""Database utilities for the Legal RAG System"""
import os
import json
from typing import Dict, List, Optional, Any
import uuid
import logging
from pathlib import Path
from datetime import datetime
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DBUtils:
    """Simple file-based database for user management"""
    
    def __init__(self, db_dir: str = "data"):
        self.db_dir = Path(db_dir)
        self.users_file = self.db_dir / "users.json"
        self._ensure_directories()
        self._ensure_files()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.db_dir.mkdir(exist_ok=True)
    
    def _ensure_files(self):
        """Ensure required files exist"""
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump([], f)
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading users file: {e}")
            return []
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        users = self.get_users()
        for user in users:
            if user["username"] == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        users = self.get_users()
        for user in users:
            if user["email"] == email:
                return user
        return None
    
    def create_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        # Check if username or email already exists
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if self.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Create user object
        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add user to database
        users = self.get_users()
        users.append(user)
        
        # Save users to file
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        # Return user without hashed_password
        user_response = user.copy()
        user_response.pop("hashed_password")
        return user_response
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user["hashed_password"]):
            return None
        
        # Return user without hashed_password
        user_response = user.copy()
        user_response.pop("hashed_password")
        return user_response

# Global database utils instance
db_utils = DBUtils()