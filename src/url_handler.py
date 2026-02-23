import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import requests
from bs4 import BeautifulSoup
from src.logger import logger

class URLHandlerError(Exception):
    pass

def fetch_article_from_url(url: str) -> str:
    logger.info(f"Fetching article from URL: {url}")
    
    if not url:
        logger.error("Empty URL provided")
        raise URLHandlerError("Please provide a valid URL")
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        logger.info(f"Added https:// prefix: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.SSLError:
            logger.warning(f"SSL verification failed, retrying without verification for: {url}")
            response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        response.raise_for_status()
        
        logger.info(f"Successfully fetched URL, status code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        title = ""
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        article_content = ""
        
        article_tag = soup.find('article')
        if article_tag:
            article_content = article_tag.get_text(separator='\n', strip=True)
        
        if not article_content:
            main_tag = soup.find('main')
            if main_tag:
                article_content = main_tag.get_text(separator='\n', strip=True)
        
        if not article_content:
            content_divs = soup.find_all('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower() or 'post' in x.lower() or 'body' in x.lower() or 'text' in x.lower() or 'entry' in x.lower()))
            for div in content_divs:
                text = div.get_text(separator='\n', strip=True)
                if len(text) > len(article_content):
                    article_content = text
        
        if not article_content:
            section_tags = soup.find_all('section')
            for section in section_tags:
                text = section.get_text(separator='\n', strip=True)
                if len(text) > len(article_content):
                    article_content = text
        
        if not article_content:
            p_tags = soup.find_all('p')
            paragraphs = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
            if paragraphs:
                article_content = '\n\n'.join(paragraphs)
        
        if not article_content:
            body = soup.find('body')
            if body:
                article_content = body.get_text(separator='\n', strip=True)
        
        article_content = '\n'.join([line for line in article_content.split('\n') if line.strip()])
        
        if len(article_content) < 50:
            logger.warning(f"Extracted content seems too short: {len(article_content)} characters")
            raise URLHandlerError("Could not extract meaningful content from this URL. The page might not contain an article or might require JavaScript rendering.")
        
        logger.info(f"Successfully extracted {len(article_content)} characters from URL")
        
        result = f"Title: {title}\n\n" if title else ""
        result += article_content
        
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching URL: {url}")
        raise URLHandlerError("The request timed out. Please try a different URL or check your connection.")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for URL: {url}")
        raise URLHandlerError("Could not connect to the URL. Please check if the URL is correct.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for URL {url}: {str(e)}")
        raise URLHandlerError(f"HTTP error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        raise URLHandlerError(f"Error fetching article: {str(e)}")
