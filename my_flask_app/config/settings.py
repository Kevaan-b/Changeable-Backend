"""
Application configuration settings.
"""
import os
from google.oauth2 import service_account

class Config:
    """Configuration class for the application."""
    
    # EasyOCR Configuration
    EASYOCR_LANGUAGES = ['en', 'ko']  # Add languages as needed
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

    # Typesetting Configuration
    TYPESETTER_ENGINE = os.getenv('TYPESETTER_ENGINE', 'opencv')

    # OpenCV Typesetting Settings
    INPAINT_METHOD = os.getenv('INPAINT_METHOD', 'INPAINT_TELEA')  # or 'INPAINT_NS'
    INPAINT_RADIUS = int(os.getenv('INPAINT_RADIUS', '3'))
    FONT_SIZE_MULTIPLIER = float(os.getenv('FONT_SIZE_MULTIPLIER', '1.0'))
    TEXT_PADDING = int(os.getenv('TEXT_PADDING', '5'))
    BACKGROUND_EXPAND = int(os.getenv('BACKGROUND_EXPAND', '2'))

    # Font Settings
    DEFAULT_FONT_PATH = os.getenv('DEFAULT_FONT_PATH', '/System/Fonts/Arial.ttf')
    MIN_FONT_SIZE = int(os.getenv('MIN_FONT_SIZE', '12'))
    MAX_FONT_SIZE = int(os.getenv('MAX_FONT_SIZE', '72'))
    MIN_TRANSLATION_CONFIDENCE = float(os.getenv('MIN_TRANSLATION_CONFIDENCE', '0.3'))

    # Text Appearance
    TEXT_COLOR = tuple(map(int, os.getenv('TEXT_COLOR', '0,0,0').split(',')))  # Black
    TEXT_OUTLINE_COLOR = tuple(map(int, os.getenv('TEXT_OUTLINE_COLOR', '255,255,255').split(',')))  # White
    TEXT_BACKGROUND_COLOR = tuple(map(int, os.getenv('TEXT_BACKGROUND_COLOR', '255,255,255,200').split(',')))  # Semi-transparent white
    TEXT_OUTLINE_WIDTH = int(os.getenv('TEXT_OUTLINE_WIDTH', '1'))
    BACKGROUND_THRESHOLD = float(os.getenv('BACKGROUND_THRESHOLD', '30.0'))

    
  

