import os
import streamlit as st
from dotenv import load_dotenv
from lib.character import Character, PsiEmotionModel
from lib.file_processor import extract_text_from_uploaded_file
from lib.memory import MemorySystem

# Load environment and configuration
load_dotenv()

# UI Configuration
st.set_page_config(page_title="AI Character Simulator", page_icon=":brain:", layout="wide")

# Initialize session state
if "characters" not in st.session_state:
    st.session_state.characters = []
if "selected_character" not in st.session_state:
    st.session_state.selected_character = None

# Main app interface
def main():
    st.title("📚 AI Character Simulator")
    
    # Sidebar setup
    with st.sidebar:
        setup_sidebar()
    
    # Main content area
    if st.session_state.selected_character:
        render_chat_interface()
    else:
        render_welcome_screen()

if __name__ == "__main__":
    main()