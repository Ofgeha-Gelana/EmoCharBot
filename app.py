import os
import streamlit as st
from dotenv import load_dotenv
from ui_components import setup_sidebar, render_chat_interface, render_welcome_screen
from character_manager import extract_characters, initialize_session_state

# Load environment and configuration
load_dotenv()

def main():
    """Main application controller"""
    # Initialize session state
    initialize_session_state()
    
    # Set up page config
    st.set_page_config(
        page_title="Literary Character Chat",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    apply_custom_styles()
    
    # Sidebar setup
    with st.sidebar:
        setup_sidebar()
    
    # Main content area
    if st.session_state.current_character:
        render_chat_interface()
    else:
        render_welcome_screen()

def apply_custom_styles():
    """Inject custom CSS for professional styling"""
    st.markdown("""
    <style>
        /* Main content area */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e1e4e8;
        }
        
        /* Chat containers */
        .stChatMessage {
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* User messages */
        [data-testid="stChatMessage"][aria-label="user"] {
            background-color: #e3f2fd;
            margin-left: 15%;
        }
        
        /* Assistant messages */
        [data-testid="stChatMessage"][aria-label="assistant"] {
            background-color: #ffffff;
            margin-right: 15%;
            border: 1px solid #e1e4e8;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #2c3e50;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #4a90e2;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        /* Input fields */
        .stTextInput>div>div>input {
            border-radius: 6px;
            padding: 8px 12px;
        }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()