import os
from datetime import datetime
from werkzeug.utils import secure_filename
from typing import Optional

class LocalStorageService:
    """Service for storing files locally instead of AWS S3"""
    
    def __init__(self, base_path: str = None):
        """
        Initialize local storage service
        
        Args:
            base_path: Base directory for file storage
        """
        if base_path is None:
            # Store in 'uploads' folder in backend directory
            base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        
        self.base_path = base_path
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self) -> bool:
        """
        Ensure the storage directory exists, create if it doesn't
        
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(self.base_path, exist_ok=True)
            # Create subdirectory for LAS files
            las_dir = os.path.join(self.base_path, 'las-files')
            os.makedirs(las_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> dict:
        """
        Copy a file to local storage
        
        Args:
            file_path: Path to file to upload
            object_name: Destination filename. If not specified, file_path basename is used
            
        Returns:
            Dictionary with storage_key and file_url
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        # Make filename safe
        object_name = secure_filename(object_name)
        
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        storage_key = f"las-files/{timestamp}_{object_name}"
        
        try:
            # Ensure directory exists
            self.ensure_directory_exists()
            
            # Create destination path
            dest_path = os.path.join(self.base_path, storage_key)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file to destination
            import shutil
            shutil.copy2(file_path, dest_path)
            
            # Generate relative URL
            file_url = f"/files/{storage_key}"
            
            return {
                'storage_key': storage_key,
                'file_url': file_url,
                'local_path': dest_path,
                'success': True
            }
            
        except Exception as e:
            print(f"Error uploading file to local storage: {e}")
            return {
                'storage_key': None,
                'file_url': None,
                'local_path': None,
                'success': False,
                'error': str(e)
            }
    
    def upload_fileobj(self, file_obj, object_name: str) -> dict:
        """
        Save a file object to local storage
        
        Args:
            file_obj: File-like object to save
            object_name: Destination filename
            
        Returns:
            Dictionary with storage_key and file_url
        """
        # Make filename safe
        object_name = secure_filename(object_name)
        
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        storage_key = f"las-files/{timestamp}_{object_name}"
        
        try:
            # Ensure directory exists
            self.ensure_directory_exists()
            
            # Create destination path
            dest_path = os.path.join(self.base_path, storage_key)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Reset file pointer to beginning
            file_obj.seek(0)
            
            # Save file object to destination
            with open(dest_path, 'wb') as f:
                f.write(file_obj.read())
            
            # Generate relative URL
            file_url = f"/files/{storage_key}"
            
            return {
                'storage_key': storage_key,
                'file_url': file_url,
                'local_path': dest_path,
                'success': True
            }
            
        except Exception as e:
            print(f"Error uploading file object to local storage: {e}")
            return {
                'storage_key': None,
                'file_url': None,
                'local_path': None,
                'success': False,
                'error': str(e)
            }
    
    def download_file(self, storage_key: str, local_path: str) -> bool:
        """
        Copy a file from storage to local path
        
        Args:
            storage_key: Storage key
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            src_path = os.path.join(self.base_path, storage_key)
            if not os.path.exists(src_path):
                print(f"File not found: {src_path}")
                return False
            
            import shutil
            shutil.copy2(src_path, local_path)
            return True
        except Exception as e:
            print(f"Error downloading file from local storage: {e}")
            return False
    
    def delete_file(self, storage_key: str) -> bool:
        """
        Delete a file from local storage
        
        Args:
            storage_key: Storage key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.base_path, storage_key)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file from local storage: {e}")
            return False
    
    def get_file_path(self, storage_key: str) -> Optional[str]:
        """
        Get the full local path for a storage key
        
        Args:
            storage_key: Storage key
            
        Returns:
            Full local path or None if not found
        """
        file_path = os.path.join(self.base_path, storage_key)
        if os.path.exists(file_path):
            return file_path
        return None
    
    def generate_presigned_url(self, storage_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a URL for accessing the file (simple relative URL for local storage)
        
        Args:
            storage_key: Storage key
            expiration: Not used for local storage
            
        Returns:
            Relative URL string
        """
        return f"/files/{storage_key}"
