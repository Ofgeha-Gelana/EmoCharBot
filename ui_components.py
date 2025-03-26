import streamlit as st
from character_manager import extract_characters
from lib.file_processor import extract_text_from_uploaded_file

def setup_sidebar():
    """Configure the professional sidebar UI"""
    st.sidebar.header("📚 Literary Character Chat")
    st.sidebar.markdown("---")
    
    # User management
    st.sidebar.subheader("Your Identity")
    st.session_state.current_user = st.sidebar.text_input(
        "Enter your name", 
        value=st.session_state.get("current_user", "Guest"),
        help="This helps the character remember conversations with you"
    )
    
    # Character source
    st.sidebar.subheader("Source Material")
    input_method = st.sidebar.radio(
        "Input method", 
        ("Upload book", "Paste text"),
        horizontal=True
    )
    
    book_text = ""
    if input_method == "Upload book":
        uploaded_file = st.sidebar.file_uploader(
            "Choose a file",
            type=["txt", "pdf"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            with st.spinner("📖 Extracting text..."):
                book_text = extract_text_from_uploaded_file(uploaded_file)
    else:
        book_text = st.sidebar.text_area(
            "Paste your text here",
            height=200,
            label_visibility="collapsed"
        )
    
    if st.sidebar.button("Analyze Text", use_container_width=True) and book_text:
        with st.spinner("🔍 Identifying characters..."):
            st.session_state.characters = extract_characters(book_text)
            if st.session_state.characters:
                st.sidebar.success(f"Found {len(st.session_state.characters)} characters")
    
    # Character selection
    if st.session_state.get("characters"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Available Characters")
        
        cols = st.sidebar.columns([3, 1])
        with cols[0]:
            selected_char = st.selectbox(
                "Select character",
                [char.name for char in st.session_state.characters],
                label_visibility="collapsed"
            )
        with cols[1]:
            if st.button("Chat", use_container_width=True):
                st.session_state.current_character = next(
                    char for char in st.session_state.characters 
                    if char.name == selected_char
                )
                st.rerun()
        
        # Character preview cards
        for char in st.session_state.characters:
            with st.sidebar.expander(f"🧑‍💼 {char.name}"):
                st.caption("Description")
                st.markdown(f"*{char.description}*")
                st.caption("Personality Traits")
                st.markdown(", ".join(char.traits))

def render_chat_interface():
    """Professional chat interface"""
    char = st.session_state.current_character
    
    # Header with character info
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"### 🧑‍💼 {char.name}")
        st.caption(f"*{char.description}*")
    with col2:
        st.markdown("**Personality Traits**: " + ", ".join(char.traits))
    
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    # Initialize chat if needed
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello {st.session_state.current_user}! I'm {char.name}. How can I help you today?"}
        ]
    
    # Display messages
    with chat_container:
        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
    
    # Input area
    with st.container():
        if prompt := st.chat_input(f"Message {char.name}..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate response
            with st.spinner(f"{char.name} is thinking..."):
                try:
                    response = generate_character_response(char, prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

def render_welcome_screen():
    """Professional welcome screen"""
    st.markdown("# 📚 Welcome to Literary Character Chat")
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
        <h3 style="color: #2c3e50;">Start chatting with characters from literature</h3>
        <p>Upload a book or paste text to begin interacting with characters</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://via.placeholder.com/800x400?text=Upload+text+or+book+to+start", 
             use_column_width=True)
    
    st.markdown("### How it works:")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        #### 1. Upload Content
        Upload a book or paste text to analyze
        """)
    with cols[1]:
        st.markdown("""
        #### 2. Select Character
        Choose from the identified characters
        """)
    with cols[2]:
        st.markdown("""
        #### 3. Start Chatting
        Have natural conversations with literary characters
        """)

def generate_character_response(character, prompt):
    """
    Generate an in-character response based on conversation history
    
    Args:
        character (Character): The character to respond
        prompt (str): User's input message
        
    Returns:
        str: Character's response
        
    Raises:
        Exception: If response generation fails
    """
    try:
        # Build conversation context
        context = f"""
        You are {character.name}, {character.description}.
        Personality traits: {', '.join(character.traits)}.
        
        Current conversation with {st.session_state.current_user}:
        {_format_conversation_history(st.session_state.messages)}
        
        Respond naturally in character to this message:
        {st.session_state.current_user}: {prompt}
        """
        
        # Generate response with safety settings
        response = gen_ai.generate_content(
            contents=[context],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 1000
            },
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
            }
        )
        
        if not response.text:
            raise ValueError("Empty response from model")
            
        return response.text
        
    except Exception as e:
        st.error("Failed to generate character response")
        st.exception(e)  # Show detailed error in debug mode
        return f"Sorry, {character.name} seems to be having trouble responding right now."

def _format_conversation_history(messages):
    """Format conversation history for context"""
    return "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" 
        for msg in messages[-10:]  # Last 10 messages for context
    )