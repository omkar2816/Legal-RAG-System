import pytesseract
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path):
    """
    Extract text from an image file using OCR
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Extracted text as string
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        logger.info(f"Successfully extracted text from image: {image_path}")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        raise

def process_image_with_ocr(file_path):
    """
    Process an image file with OCR to extract text
    
    Args:
        file_path: Path to the image file
    
    Returns:
        Extracted text as string
    """
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Validate file is an image
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in valid_extensions:
            raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {', '.join(valid_extensions)}")
        
        # Extract text using OCR
        text = extract_text_from_image(file_path)
        
        # Clean up the extracted text
        if text:
            # Remove extra whitespace and normalize
            text = ' '.join(text.split())
            logger.info(f"Successfully processed image with OCR: {file_path}")
        else:
            logger.warning(f"No text extracted from image: {file_path}")
        
        return text
        
    except Exception as e:
        logger.error(f"Error processing image with OCR {file_path}: {e}")
        raise