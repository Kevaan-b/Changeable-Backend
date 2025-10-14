"""
Application configuration settings.
"""
import os
from google.oauth2 import service_account

class Config:
    """Configuration class for the application."""
    
    # EasyOCR Configuration
    EASYOCR_LANGUAGES = ['en', 'ja']  # Add languages as needed
    USE_GPU_OCR = os.getenv('USE_GPU_OCR', 'false').lower() == 'true'
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', '0.6'))
    OCR_ENHANCE_IMAGE = os.getenv('OCR_ENHANCE_IMAGE', 'true').lower() == 'true'
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_FLASH_MODEL = os.getenv('GEMINI_FLASH_MODEL', 'gemini-2.5-flash')
    GEMINI_PRO_MODEL = os.getenv('GEMINI_PRO_MODEL', 'gemini-2.5-pro')
    
    # Translation Configuration
    TRANSLATION_MAX_RETRIES = int(os.getenv('TRANSLATION_MAX_RETRIES', '3'))
    TRANSLATION_RETRY_DELAY = int(os.getenv('TRANSLATION_RETRY_DELAY', '2'))
    
    # Google Translate Configuration
    GOOGLE_TRANSLATE_CREDENTIALS = None
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        GOOGLE_TRANSLATE_CREDENTIALS = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'zip'}
    
  

