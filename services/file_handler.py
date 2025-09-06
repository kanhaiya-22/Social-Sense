import os
import logging
from werkzeug.utils import secure_filename
import uuid

logger = logging.getLogger(__name__)

class FileHandler:
    """Service for handling file uploads and validation"""
    
    def __init__(self, upload_folder, allowed_extensions):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f"File handler initialized with upload folder: {upload_folder}")
    
    def is_allowed_file(self, filename):
        """
        Check if file extension is allowed
        
        Args:
            filename (str): Name of the file
            
        Returns:
            bool: True if file extension is allowed
        """
        if not filename:
            return False
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file(self, file):
        """
        Validate uploaded file
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file or file.filename == '':
                return False, "No file provided"
            
            # Check file extension
            if not self.is_allowed_file(file.filename):
                return False, f"Invalid file type. Allowed types: {', '.join(self.allowed_extensions)}"
            
            # Check file size (if possible)
            if hasattr(file, 'content_length') and file.content_length:
                if file.content_length > self.max_file_size:
                    return False, f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            
            # Check file content by reading a small portion
            file.seek(0)
            header = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset file pointer
            
            if not header:
                return False, "File appears to be empty"
            
            # Basic file type validation based on headers
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            if file_extension == 'pdf' and not header.startswith(b'%PDF'):
                return False, "File does not appear to be a valid PDF"
            
            if file_extension in ['jpg', 'jpeg'] and not (header.startswith(b'\xff\xd8\xff') or b'JFIF' in header[:20]):
                return False, "File does not appear to be a valid JPEG"
            
            if file_extension == 'png' and not header.startswith(b'\x89PNG\r\n\x1a\n'):
                return False, "File does not appear to be a valid PNG"
            
            return True, "File is valid"
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False, f"File validation failed: {str(e)}"
    
    def save_file(self, file):
        """
        Save uploaded file to upload directory
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            str: Saved filename or None if failed
        """
        try:
            # Validate file first
            is_valid, error_msg = self.validate_file(file)
            if not is_valid:
                logger.error(f"File validation failed: {error_msg}")
                return None
            
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Save file
            filepath = os.path.join(self.upload_folder, unique_filename)
            file.save(filepath)
            
            # Verify file was saved successfully
            if not os.path.exists(filepath):
                logger.error(f"File was not saved successfully: {filepath}")
                return None
            
            # Check saved file size
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                logger.error(f"Saved file is empty: {filepath}")
                self.cleanup_file(filepath)
                return None
            
            if file_size > self.max_file_size:
                logger.error(f"Saved file exceeds size limit: {file_size} bytes")
                self.cleanup_file(filepath)
                return None
            
            logger.info(f"File saved successfully: {unique_filename} ({file_size} bytes)")
            return unique_filename
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return None
    
    def cleanup_file(self, filepath):
        """
        Remove uploaded file after processing
        
        Args:
            filepath (str): Path to file to remove
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File cleaned up: {filepath}")
            else:
                logger.warning(f"File not found for cleanup: {filepath}")
                
        except Exception as e:
            logger.error(f"Error cleaning up file {filepath}: {str(e)}")
    
    def get_file_info(self, filepath):
        """
        Get information about a file
        
        Args:
            filepath (str): Path to the file
            
        Returns:
            dict: File information or None if file doesn't exist
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            stat = os.stat(filepath)
            filename = os.path.basename(filepath)
            
            return {
                'filename': filename,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024*1024), 2),
                'modified': stat.st_mtime,
                'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
                'path': filepath
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {filepath}: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_hours=24):
        """
        Clean up old uploaded files
        
        Args:
            max_age_hours (int): Maximum age of files to keep in hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            if not os.path.exists(self.upload_folder):
                return
            
            cleaned_count = 0
            for filename in os.listdir(self.upload_folder):
                if filename.startswith('.'):  # Skip hidden files
                    continue
                
                filepath = os.path.join(self.upload_folder, filename)
                
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old file: {filename}")
                        
                except Exception as file_error:
                    logger.warning(f"Could not clean up file {filename}: {str(file_error)}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old files")
                
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
