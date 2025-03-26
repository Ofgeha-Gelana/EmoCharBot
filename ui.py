import streamlit as st
from lib.character import Character

def setup_page():
    """Configure the page with professional styling"""
    st.set_page_config(
        page_title="Character Chat Simulator",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional look
    st.markdown("""
    <style>
        .main {background-color: #f8f9fa;}
        .sidebar .sidebar-content {background-color: #ffffff;}
        h1 {color: #2c3e50;}
        h2 {color: #3498db;}
        .stTextInput input, .stSelectbox select {border-radius: 5px;}
        .stButton button {border-radius: 5px; background-color: #3498db; color: white;}
        .stAlert {border-radius: 5px;}
        .chat-message {padding: 10px; border-radius: 10px; margin: 5px 0;}
        .user-message {background-color: #e3f2fd;}
        .assistant-message {background-color: #f5f5f5;}
    </style>
    """, unsafe_allow_html=True)

def create_sidebar(characters: list[Character], current_character: Character):
    """Create the professional sidebar UI"""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x80?text=Character+Chat", use_column_width=True)
        st.markdown("---")
        
        # User section
        with st.expander("👤 User Profile", expanded=True):
            current_user = st.text_input(
                "Your Name", 
                value=st.session_state.get("current_user", "Ofgeha"),
                help="Enter your name to personalize the conversation"
            )
            st.session_state.current_user = current_user
        
        # Character selection
        with st.expander("🧙 Character Selection", expanded=True):
            if characters:
                selected_char = st.selectbox(
                    "Choose Character",
                    options=[char.name for char in characters],
                    index=[char.name for char in characters].index(current_character.name) if current_character else 0,
                    key="char_select"
                )
                
                if st.button("Switch Character", use_container_width=True):
                    st.session_state.current_character = next(char for char in characters if char.name == selected_char)
                    st.rerun()
                
                if current_character:
                    st.markdown("---")
                    st.markdown(f"**Name:** {current_character.name}")
                    st.markdown(f"**About:** {current_character.description}")
                    st.markdown("**Personality:**")
                    for trait in current_character.traits:
                        st.markdown(f"- {trait}")
        
        # File upload section
        with st.expander("📚 Upload Source", expanded=True):
            setup_file_upload()

def setup_file_upload():
    """File upload UI component"""
    input_method = st.radio("Input method:", ("Paste text", "Upload file"), horizontal=True)
    
    book_text = ""
    if input_method == "Paste text":
        book_text = st.text_area("Paste your text here:", height=150)
    else:
        uploaded_file = st.file_uploader("Choose a file:", type=["txt", "pdf"])
        if uploaded_file:
            with st.spinner("Processing file..."):
                book_text = extract_text_from_uploaded_file(uploaded_file)
                if book_text:
                    st.success("File processed successfully!")
    
    if st.button("Extract Characters", use_container_width=True) and book_text:
        with st.spinner("Analyzing content..."):
            st.session_state.characters = extract_characters(book_text)
            if st.session_state.characters:
                st.session_state.current_character = st.session_state.characters[0]
                st.success(f"Found {len(st.session_state.characters)} characters")
                st.rerun()

def display_chat_header(character: Character):
    """Display professional chat header"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://via.placeholder.com/150?text=Avatar", width=100)
    with col2:
        st.markdown(f"## {character.name}")
        st.caption(f"*{character.description}*")
    st.markdown("---")

def display_message(msg):
    """Display a chat message with professional styling"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{msg['role'].title()}**")
    with col2:
        with st.container():
            st.markdown(f"""
            <div class="chat-message {'user-message' if msg['role'] == 'user' else 'assistant-message'}">
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)

def display_conversation_history(messages):
    """Display the entire conversation thread"""
    for msg in messages:
        display_message(msg)

def display_user_input(character: Character):
    """Display the user input area"""
    with st.form("chat_input", clear_on_submit=True):
        prompt = st.text_area(
            f"Message {character.name}...",
            key="input",
            height=100,
            max_chars=1000,
            placeholder="Type your message here..."
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)
    
    if submitted and prompt:
        return prompt
    return None