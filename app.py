import streamlit as st
import time
from src.logger import logger
from src.personality import get_greeting, get_name
from src.url_handler import fetch_article_from_url, URLHandlerError
from src.pdf_handler import extract_text_from_pdf, PDFHandlerError
from src.summarizer import get_summarizer, SummarizerError

st.set_page_config(
    page_title=f"{get_name()} - AI Assistant",
    page_icon="🤖",
    layout="wide"
)

def show_loading(message: str):
    return st.empty()

def show_loading_spinner(message: str):
    return st.spinner(f"⏳ {message}")

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "greeting_shown" not in st.session_state:
        st.session_state.greeting_shown = False
    if "current_pdf_text" not in st.session_state:
        st.session_state.current_pdf_text = None
    if "current_pdf_name" not in st.session_state:
        st.session_state.current_pdf_name = None

def clear_chat():
    st.session_state.messages = []
    st.session_state.greeting_shown = False
    st.session_state.current_pdf_text = None
    st.session_state.current_pdf_name = None

def show_greeting():
    if not st.session_state.greeting_shown:
        st.chat_message("assistant").markdown(get_greeting())
        st.session_state.greeting_shown = True

def handle_url_summarization(url: str):
    try:
        loading_placeholder = st.empty()
        loading_placeholder.info("🔄 Fetching article from URL... Please wait...")
        
        article_text = fetch_article_from_url(url)
        loading_placeholder.empty()
        
        loading_placeholder.info("✍️ Summarizing article... Please wait...")
        
        summarizer = get_summarizer()
        summary = summarizer.summarize_text(article_text)
        loading_placeholder.empty()
        
        st.session_state.messages.append({"role": "user", "content": f"🔗 Summarize URL: {url}"})
        st.session_state.messages.append({"role": "assistant", "content": f"**📝 Article Summary:**\n\n{summary}"})
        
        st.success("✅ Summary generated successfully!")
        st.chat_message("assistant").markdown(f"**📝 Article Summary:**\n\n{summary}")
        
    except URLHandlerError as e:
        st.error(f"❌ Error fetching URL: {str(e)}")
        logger.error(f"URL Handler Error: {str(e)}")
    except SummarizerError as e:
        st.error(f"❌ Error summarizing: {str(e)}")
        logger.error(f"Summarizer Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error in URL summarization: {str(e)}")

def handle_pdf_summarization(pdf_file):
    try:
        loading_placeholder = st.empty()
        loading_placeholder.info("📄 Extracting text from PDF... Please wait...")
        
        pdf_text = extract_text_from_pdf(pdf_file)
        loading_placeholder.empty()
        
        loading_placeholder.info("✍️ Summarizing PDF... Please wait...")
        
        summarizer = get_summarizer()
        summary = summarizer.summarize_text(pdf_text)
        loading_placeholder.empty()
        
        st.session_state.current_pdf_text = pdf_text
        st.session_state.current_pdf_name = pdf_file.name
        
        st.session_state.messages.append({"role": "user", "content": f"📄 Summarize PDF: {pdf_file.name}"})
        st.session_state.messages.append({"role": "assistant", "content": f"**📄 PDF Summary:**\n\n{summary}"})
        
        st.success("✅ PDF Summary generated! You can now ask questions about this PDF below.")
        st.chat_message("assistant").markdown(f"**📄 PDF Summary:**\n\n{summary}")
        
    except PDFHandlerError as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        logger.error(f"PDF Handler Error: {str(e)}")
    except SummarizerError as e:
        st.error(f"❌ Error summarizing: {str(e)}")
        logger.error(f"Summarizer Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error in PDF summarization: {str(e)}")

def handle_chat(user_message: str):
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    try:
        loading_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        loading_placeholder.info("🤔 EIT is thinking... Please wait...")
        progress_bar.progress(25)
        
        summarizer = get_summarizer()
        history = [
            {"user": m["content"], "assistant": st.session_state.messages[i+1]["content"]}
            for i, m in enumerate(st.session_state.messages[:-1])
            if m["role"] == "user" and i + 1 < len(st.session_state.messages) and st.session_state.messages[i+1]["role"] == "assistant"
        ]
        
        progress_bar.progress(50)
        loading_placeholder.info("💭 Generating response...")
        
        response = summarizer.chat(user_message, history)
        
        progress_bar.progress(100)
        loading_placeholder.empty()
        progress_bar.empty()
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)
        
    except SummarizerError as e:
        st.error(f"❌ Error: {str(e)}")
        logger.error(f"Chat Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error in chat: {str(e)}")

def handle_pdf_chat(user_message: str, pdf_text: str, pdf_name: str):
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    try:
        loading_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        loading_placeholder.info("🤔 EIT is analyzing the PDF... Please wait...")
        progress_bar.progress(25)
        
        summarizer = get_summarizer()
        
        progress_bar.progress(50)
        loading_placeholder.info("💭 Generating response based on PDF content...")
        
        response = summarizer.chat_about_pdf(user_message, pdf_text)
        
        progress_bar.progress(100)
        loading_placeholder.empty()
        progress_bar.empty()
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)
        
    except SummarizerError as e:
        st.error(f"❌ Error: {str(e)}")
        logger.error(f"PDF Chat Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error in PDF chat: {str(e)}")

def main():
    init_session_state()
    
    st.title(f"🤖 {get_name()} - AI Assistant")
    st.markdown("---")
    
    with st.spinner("🤖 Loading EIT Assistant..."):
        time.sleep(0.5)
    
    show_greeting()
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            clear_chat()
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown("### 📌 Choose an option:")
    
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔗 URL Summary", "📄 PDF Summary"])
    
    with tab1:
        if prompt := st.chat_input("Type your message here..."):
            st.chat_message("user").markdown(prompt)
            handle_chat(prompt)
    
    with tab2:
        with st.form("url_form"):
            url_input = st.text_input("Enter article URL:", placeholder="https://example.com/article")
            submit_url = st.form_submit_button("Summarize URL")
            
            if submit_url and url_input:
                handle_url_summarization(url_input)
            elif submit_url and not url_input:
                st.warning("Please enter a URL")
    
    with tab3:
        with st.form("pdf_form"):
            pdf_input = st.file_uploader("Upload a PDF file:", type=["pdf"])
            submit_pdf = st.form_submit_button("Summarize PDF")
            
            if submit_pdf and pdf_input:
                handle_pdf_summarization(pdf_input)
            elif submit_pdf and not pdf_input:
                st.warning("Please upload a PDF file")
        
        if st.session_state.current_pdf_text:
            st.divider()
            st.markdown(f"### 💬 Chat about: *{st.session_state.current_pdf_name}*")
            
            pdf_chat_key = f"pdf_chat_{st.session_state.current_pdf_name}"
            
            if pdf_chat_key not in st.session_state:
                st.session_state[pdf_chat_key] = []
            
            for msg in st.session_state[pdf_chat_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if pdf_chat_prompt := st.chat_input(f"Ask questions about {st.session_state.current_pdf_name}..."):
                st.chat_message("user").markdown(pdf_chat_prompt)
                
                st.session_state[pdf_chat_key].append({"role": "user", "content": pdf_chat_prompt})
                
                handle_pdf_chat(pdf_chat_prompt, st.session_state.current_pdf_text, st.session_state.current_pdf_name)
                
                response = st.session_state.messages[-1]["content"]
                st.session_state[pdf_chat_key].append({"role": "assistant", "content": response})

if __name__ == "__main__":
    logger.info("Starting EIT Assistant application")
    main()
