import os
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class TextExtractor:
    """Service for extracting text from various file formats"""
    
    def __init__(self):
        self.setup_tesseract()
    
    def setup_tesseract(self):
        """Configure tesseract OCR"""
        try:
            # Try to use tesseract from system
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.warning(f"Tesseract setup warning: {e}")
    
    def extract_from_pdf(self, filepath):
        """
        Extract text from PDF file using PyMuPDF
        
        Args:
            filepath (str): Path to PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"PDF file not found: {filepath}")
            
            text_content = []
            
            # Open PDF document
            with fitz.open(filepath) as doc:
                logger.info(f"Processing PDF with {len(doc)} pages")
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    if text.strip():
                        text_content.append(text)
                        logger.debug(f"Extracted {len(text)} characters from page {page_num + 1}")
            
            full_text = "\n\n".join(text_content).strip()
            
            if not full_text:
                logger.warning("No text extracted from PDF")
                return ""
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filepath}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_from_image(self, filepath):
        """
        Extract text from image file using OCR
        
        Args:
            filepath (str): Path to image file
            
        Returns:
            str: Extracted text content
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Image file not found: {filepath}")
            
            # Open and process image
            with Image.open(filepath) as image:
                logger.info(f"Processing image: {image.size} pixels, mode: {image.mode}")
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Configure OCR parameters
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?@#$%^&*()_+-=[]{}|;:,.<>?'
                
                # Extract text using OCR
                extracted_text = pytesseract.image_to_string(
                    image, 
                    config=custom_config,
                    lang='eng'
                ).strip()
                
                if not extracted_text:
                    logger.warning("No text detected in image")
                    return ""
                
                # Clean up extracted text
                cleaned_text = self._clean_ocr_text(extracted_text)
                
                logger.info(f"Successfully extracted {len(cleaned_text)} characters from image")
                return cleaned_text
                
        except Exception as e:
            logger.error(f"Error extracting text from image {filepath}: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def _clean_ocr_text(self, text):
        """
        Clean and normalize OCR-extracted text
        
        Args:
            text (str): Raw OCR text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = []
        for line in text.split('\n'):
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                lines.append(cleaned_line)
        
        # Join lines with single newlines
        cleaned_text = '\n'.join(lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip()
    
    def get_text_preview(self, text, max_chars=200):
        """
        Get a preview of extracted text
        
        Args:
            text (str): Full text content
            max_chars (int): Maximum characters in preview
            
        Returns:
            str: Text preview
        """
        if not text:
            return ""
        
        if len(text) <= max_chars:
            return text
        
        # Find a good breaking point near the limit
        preview = text[:max_chars]
        last_space = preview.rfind(' ')
        
        if last_space > max_chars * 0.8:  # If space is reasonably close to limit
            preview = preview[:last_space]
        
        return preview + "..."
