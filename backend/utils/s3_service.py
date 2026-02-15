import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
from typing import Optional


class S3Service:
    """Service for interacting with Amazon S3"""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")
    
    def ensure_bucket_exists(self) -> bool:
        """
        Ensure the S3 bucket exists, create if it doesn't
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, try to create it
                try:
                    if os.getenv('AWS_REGION') == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': os.getenv('AWS_REGION')
                            }
                        )
                    print(f"Created S3 bucket: {self.bucket_name}")
                    return True
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    return False
            else:
                print(f"Error checking bucket: {e}")
                return False
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> dict:
        """
        Upload a file to S3
        
        Args:
            file_path: Path to file to upload
            object_name: S3 object name. If not specified, file_path basename is used
            
        Returns:
            Dictionary with s3_key and s3_url
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"las-files/{timestamp}_{object_name}"
        
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists()
            
            # Upload file
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            
            # Generate URL
            s3_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{s3_key}"
            
            return {
                's3_key': s3_key,
                's3_url': s3_url,
                'success': True
            }
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return {
                's3_key': None,
                's3_url': None,
                'success': False,
                'error': str(e)
            }
    
    def upload_fileobj(self, file_obj, object_name: str) -> dict:
        """
        Upload a file object to S3
        
        Args:
            file_obj: File-like object to upload
            object_name: S3 object name
            
        Returns:
            Dictionary with s3_key and s3_url
        """
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"las-files/{timestamp}_{object_name}"
        
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists()
            
            # Reset file pointer to beginning
            file_obj.seek(0)
            
            # Upload file object
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key)
            
            # Generate URL
            s3_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{s3_key}"
            
            return {
                's3_key': s3_key,
                's3_url': s3_url,
                'success': True
            }
            
        except ClientError as e:
            print(f"Error uploading file object to S3: {e}")
            return {
                's3_key': None,
                's3_url': None,
                'success': False,
                'error': str(e)
            }
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3
        
        Args:
            s3_key: S3 object key
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: Time in seconds for URL to remain valid
            
        Returns:
            Presigned URL string or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
