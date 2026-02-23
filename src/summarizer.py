import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.logger import logger
from src.personality import get_personality_prompt

load_dotenv()

class SummarizerError(Exception):
    pass

class ArticleSummarizer:
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
                raise SummarizerError("GEMINI_API_KEY not found. Please set it in .env file.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3-flash-preview')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        logger.info(f"Summarizing text of length {len(text)} characters")
        
        if not text or not text.strip():
            logger.error("Empty text provided for summarization")
            raise SummarizerError("No text provided for summarization.")
        
        try:
            prompt = f"""{get_personality_prompt()}

Please summarize the following article concisely. 
Provide a clear summary that captures the main points, key findings, and important details.
Keep the summary around {max_length} words or less, but make sure it's comprehensive.

Article to summarize:
---
{text}
---

Summary:"""
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.warning("Empty response from Gemini model")
                raise SummarizerError("Failed to generate summary. Please try again.")
            
            logger.info(f"Successfully generated summary of {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            raise SummarizerError(f"Summarization failed: {str(e)}")
    
    def chat(self, message: str, history: list = None) -> str:
        logger.info(f"Chat message received: {message[:50]}...")
        
        if not message or not message.strip():
            raise SummarizerError("Please provide a message.")
        
        try:
            history = history or []
            
            prompt = f"""{get_personality_prompt()}

Conversation history:
{chr(10).join([f"User: {h['user']}\nEIT: {h['assistant']}" for h in history])}

User: {message}

EIT:"""
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise SummarizerError("Failed to generate response. Please try again.")
            
            logger.info("Successfully generated chat response")
            return response.text
            
        except Exception as e:
            logger.error(f"Error during chat: {str(e)}")
            raise SummarizerError(f"Chat failed: {str(e)}")

summarizer = None

def get_summarizer() -> ArticleSummarizer:
    global summarizer
    if summarizer is None:
        summarizer = ArticleSummarizer()
    return summarizer
