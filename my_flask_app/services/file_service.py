"""
File handling and management utilities.
"""


class FileService:
    """Handles file uploads and extraction."""
    
    def extract_images_from_upload(self, files):
        """Extract images from uploaded files or zip archives."""
        raise NotImplementedError
    
    def _extract_from_zip(self, zip_file):
        """Extract images from zip file."""
        raise NotImplementedError
    
    def _save_temp_file(self, file):
        """Save uploaded file to temporary location."""
        raise NotImplementedError
