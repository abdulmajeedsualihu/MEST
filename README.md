# EIT - AI Assistant

EIT is an AI Assistant created by Abdul Majeed Sualihu from Ghana. It can summarize articles from URLs and PDFs, and engage in conversation.

## Features

- **Chat**: Have a conversation with EIT
- **URL Summarization**: Paste a link to an article and get a summary
- **PDF Summarization**: Upload a PDF document and get a summary
- **Personality**: EIT has a unique personality based on its creator

## Prerequisites

- Python 3.8 or higher
- Google Gemini API Key

## Installation

1. **Clone the repository**
   ```bash
   cd Week8
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   
   Open the `.env` file and replace `your_api_key_here` with your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   
   To get a Gemini API key:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy it to the `.env` file

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Usage

### Chat with EIT
- Type your message in the "Chat" tab
- EIT will respond based on its personality

### Summarize a URL
1. Go to the "URL Summary" tab
2. Paste the article URL
3. Click "Summarize URL"
4. EIT will fetch and summarize the article

### Summarize a PDF
1. Go to the "PDF Summary" tab
2. Upload a PDF file
3. Click "Summarize PDF"
4. EIT will extract text and summarize the PDF

## Project Structure

```
Week8/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .env                # Environment variables (API keys)
├── src/
│   ├── __init__.py
│   ├── logger.py       # Logging configuration
│   ├── personality.py  # EIT's personality
│   ├── url_handler.py  # URL fetching & parsing
│   ├── pdf_handler.py  # PDF text extraction
│   └── summarizer.py   # Gemini summarization
└── logs/               # Application logs
```

## Logs

Logs are stored in the `logs/` directory. Check `logs/eit_assistant.log` for application logs.

## Error Handling

The application handles errors gracefully with user-friendly messages. All errors are logged to the log file.

## License

MIT License
