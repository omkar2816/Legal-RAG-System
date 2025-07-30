"""
File utility functions for the Legal RAG System
"""
import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    """Utility class for file operations"""
    
    def __init__(self, upload_dir: str = "uploads", processed_dir: str = "processed"):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.upload_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to upload directory
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Path to saved file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}_{file_hash}{ext}"
        
        file_path = self.upload_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        return str(file_path)
    
    def move_to_processed(self, file_path: str, doc_id: str) -> str:
        """
        Move file to processed directory
        
        Args:
            file_path: Path to file
            doc_id: Document ID
        
        Returns:
            New file path
        """
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create processed file path
        name, ext = os.path.splitext(source_path.name)
        processed_filename = f"{doc_id}{ext}"
        processed_path = self.processed_dir / processed_filename
        
        # Move file
        shutil.move(str(source_path), str(processed_path))
        
        logger.info(f"Moved file to processed: {processed_path}")
        return str(processed_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information
        
        Args:
            file_path: Path to file
        
        Returns:
            File information dictionary
        """
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        return {
            "filename": path.name,
            "file_path": str(path),
            "file_size": stat.st_size,
            "file_type": path.suffix.lower(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_hash": self._calculate_file_hash(file_path)
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate MD5 hash of file
        
        Args:
            file_path: Path to file
        
        Returns:
            File hash
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def cleanup_old_files(self, max_age_days: int = 7):
        """
        Clean up old files from upload directory
        
        Args:
            max_age_days: Maximum age of files in days
        """
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
    
    def list_processed_files(self) -> List[Dict[str, Any]]:
        """
        List all processed files
        
        Returns:
            List of file information dictionaries
        """
        files = []
        for file_path in self.processed_dir.iterdir():
            if file_path.is_file():
                files.append(self.get_file_info(str(file_path)))
        return files
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to file
        
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

# Global file utils instance
file_utils = FileUtils() 