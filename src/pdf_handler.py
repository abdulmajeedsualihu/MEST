import io
from PyPDF2 import PdfReader
from src.logger import logger

class PDFHandlerError(Exception):
    pass

def extract_text_from_pdf(pdf_file) -> str:
    logger.info(f"Extracting text from PDF file")
    
    try:
        if hasattr(pdf_file, 'read'):
            file_content = pdf_file.read()
            pdf_file = io.BytesIO(file_content)
        
        reader = PdfReader(pdf_file)
        
        if len(reader.pages) == 0:
            logger.error("PDF has no pages")
            raise PDFHandlerError("The PDF file appears to be empty or corrupted.")
        
        logger.info(f"PDF has {len(reader.pages)} pages")
        
        full_text = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    full_text.append(text)
                    logger.debug(f"Extracted {len(text)} characters from page {page_num + 1}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                continue
        
        combined_text = '\n\n'.join(full_text)
        
        if not combined_text.strip():
            logger.warning("No text could be extracted from PDF")
            raise PDFHandlerError("Could not extract text from this PDF. It might contain only images or use OCR.")
        
        logger.info(f"Successfully extracted {len(combined_text)} characters from PDF")
        
        return combined_text
        
    except PDFHandlerError:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise PDFHandlerError(f"Error processing PDF: {str(e)}")
