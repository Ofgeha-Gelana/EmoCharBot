# import os
# import streamlit as st
# from dotenv import load_dotenv
# import google.generativeai as gen_ai
# from lib.character import Character, PsiEmotionModel
# from lib.file_processor import extract_text_from_uploaded_file
# from lib.memory import MemorySystem

# # Load environment and configuration
# load_dotenv()

# # Configure Gemini-Pro
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# gen_ai.configure(api_key=GOOGLE_API_KEY)
# model = gen_ai.GenerativeModel('gemini-1.5-flash')

# # UI Configuration
# st.set_page_config(page_title="AI Character Simulator", page_icon=":brain:", layout="wide")

# # Initialize session state
# if "characters" not in st.session_state:
#     st.session_state.characters = []
# if "selected_character" not in st.session_state:
#     st.session_state.selected_character = None
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# def setup_sidebar():
#     """Configure the sidebar UI"""
#     st.header("Character Setup")
    
#     # Text input or upload for book
#     input_method = st.radio("Input method:", ("Paste text", "Upload file"))
    
#     book_text = ""
#     if input_method == "Paste text":
#         book_text = st.text_area("Paste book text:", height=200)
#     else:
#         uploaded_file = st.file_uploader("Upload book/text file:", type=["txt", "pdf"])
#         if uploaded_file:
#             book_text = extract_text_from_uploaded_file(uploaded_file)
#             if book_text:
#                 st.success("File successfully loaded!")
    
#     if st.button("Extract Characters") and book_text:
#         with st.spinner("Analyzing text for characters..."):
#             # This would call your character extraction logic
#             # For now we'll mock it
#             st.session_state.characters = [
#                 Character("Example", "Sample character", ["kind", "wise"])
#             ]
    
#     if st.session_state.characters:
#         character_names = [char.name for char in st.session_state.characters]
#         selected = st.selectbox("Select a character:", character_names)
#         st.session_state.selected_character = next(
#             char for char in st.session_state.characters if char.name == selected
#         )
        
#         # Display character info
#         if st.session_state.selected_character:
#             char = st.session_state.selected_character
#             st.subheader("Character Info")
#             st.markdown(f"**Name:** {char.name}")
#             st.markdown(f"**Description:** {char.description}")
#             st.markdown("**Traits:** " + ", ".join(char.traits))

# def render_chat_interface():
#     """Render the main chat interface"""
#     char = st.session_state.selected_character
    
#     st.header(f"Chatting with {char.name}")
#     st.caption(f"{char.description}")
    
#     # Display chat history
#     for msg in st.session_state.chat_history:
#         role = "assistant" if msg["role"] == "character" else "user"
#         with st.chat_message(role):
#             st.markdown(msg["content"])
    
#     # User input
#     user_input = st.chat_input(f"Talk to {char.name}...")
#     if user_input:
#         # Add user message to history
#         st.session_state.chat_history.append({
#             "role": "user",
#             "content": user_input
#         })
        
#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(user_input)
        
#         # Generate character response
#         try:
#             with st.spinner(f"{char.name} is thinking..."):
#                 response = model.generate_content(f"Respond as {char.name}: {user_input}")
#                 char_response = response.text
            
#             # Add to chat history
#             st.session_state.chat_history.append({
#                 "role": "character",
#                 "content": char_response
#             })
            
#             # Display character response
#             with st.chat_message("assistant"):
#                 st.markdown(char_response)
            
#         except Exception as e:
#             st.error(f"Error generating response: {e}")

# def render_welcome_screen():
#     """Show welcome screen when no character is selected"""
#     st.info("Please upload or paste text and extract characters to begin chatting.")
#     st.image("https://via.placeholder.com/600x300?text=Upload+a+book+or+paste+text+to+start", 
#              use_column_width=True)

# # Main app interface
# def main():
#     st.title("📚 AI Character Simulator")
    
#     # Sidebar setup
#     with st.sidebar:
#         setup_sidebar()
    
#     # Main content area
#     if st.session_state.selected_character:
#         render_chat_interface()
#     else:
#         render_welcome_screen()

# if __name__ == "__main__":
#     main()








import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from lib.character import Character
from lib.file_processor import extract_text_from_uploaded_file

# Load environment and configuration
load_dotenv()

# Configure Gemini-Pro
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-1.5-flash')

# UI Configuration
st.set_page_config(page_title="AI Character Simulator", page_icon=":brain:", layout="wide")

def extract_characters(text: str) -> list[Character]:
    """Extract characters from text using Gemini with robust JSON handling"""
    if not text.strip():
        return []

    prompt = f"""
    Analyze this text and extract significant characters. For each character provide:
    - name (string)
    - description (string)
    - traits (list of strings)
    
    Return ONLY a valid JSON array of objects formatted EXACTLY like this:
    [
        {{
            "name": "Character Name",
            "description": "Character's role and key features",
            "traits": ["trait1", "trait2", "trait3"]
        }}
    ]
    
    Text to analyze:
    {text[:20000]}  # First 20k chars for demo
    """
    
    try:
        response = model.generate_content(prompt)
        
        # First try to parse directly
        try:
            characters_data = json.loads(response.text)
        except json.JSONDecodeError:
            # If direct parse fails, try to extract JSON from markdown
            json_str = response.text.strip().strip('```json').strip('```').strip()
            characters_data = json.loads(json_str)
            
        # Validate the structure
        if not isinstance(characters_data, list):
            raise ValueError("Expected list of characters")
            
        return [
            Character(
                name=char.get('name', 'Unnamed'),
                description=char.get('description', 'No description'),
                traits=char.get('traits', [])
            ) for char in characters_data
        ]
        
    except Exception as e:
        st.error(f"Failed to extract characters. Please try again. Error: {str(e)}")
        st.text_area("Debug - AI Response", response.text, height=200)
        return []

def setup_sidebar():
    """Configure the sidebar UI for character selection"""
    st.header("📖 Source Material")
    
    input_method = st.radio("Input method:", ("Paste text", "Upload file"), index=0)
    book_text = ""
    
    if input_method == "Paste text":
        book_text = st.text_area("Paste book text:", height=200, key="paste_area")
    else:
        uploaded_file = st.file_uploader("Upload file:", type=["txt", "pdf"])
        if uploaded_file:
            with st.spinner("Extracting text..."):
                book_text = extract_text_from_uploaded_file(uploaded_file)
                if book_text:
                    st.success(f"✅ Extracted {len(book_text)} characters")
    
    if st.button("Analyze for Characters") and book_text:
        with st.spinner("Identifying characters..."):
            st.session_state.characters = extract_characters(book_text)
            if st.session_state.characters:
                st.success(f"Found {len(st.session_state.characters)} characters")

def render_character_selection():
    """Show character selection dropdown"""
    if st.session_state.characters:
        st.subheader("👥 Select Character")
        character_names = [char.name for char in st.session_state.characters]
        selected = st.selectbox("Choose a character:", character_names, key="char_select")
        st.session_state.selected_character = next(
            char for char in st.session_state.characters if char.name == selected
        )
        
        # Show character info
        char = st.session_state.selected_character
        st.markdown(f"**Description:** {char.description}")
        st.markdown(f"**Personality:** {', '.join(char.traits)}")
        
        if st.button("Start Chatting"):
            st.session_state.chat_started = True
            st.rerun()

def render_chat_interface():
    """Main chat interface with selected character"""
    char = st.session_state.selected_character
    
    st.header(f"💬 Chatting with {char.name}")
    st.caption(f"Personality: {', '.join(char.traits)}")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! I'm {char.name}. How would you like to talk?"}
        ]
    
    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    # Handle user input
    if prompt := st.chat_input(f"Talk to {char.name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Generate character response
        with st.spinner(f"{char.name} is thinking..."):
            try:
                context = f"""
                You are {char.name}, {char.description}.
                Personality traits: {', '.join(char.traits)}.
                Respond naturally in character.
                """
                response = model.generate_content([context, prompt])
                msg = response.text
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.chat_message("assistant").write(msg)
            except Exception as e:
                st.error(f"Error generating response: {e}")

# def main():
#     """Main app controller"""
#     # Initialize session state
#     if "characters" not in st.session_state:
#         st.session_state.characters = []
#     if "selected_character" not in st.session_state:
#         st.session_state.selected_character = None
#     if "chat_started" not in st.session_state:
#         st.session_state.chat_started = False
    
#     # Sidebar - always visible
#     with st.sidebar:
#         setup_sidebar()
#         if st.session_state.characters and not st.session_state.chat_started:
#             render_character_selection()
    
#     # Main content area
#     if st.session_state.chat_started and st.session_state.selected_character:
#         render_chat_interface()
#     else:
#         st.info("👈 Upload a book or paste text to begin")
#         st.image("https://via.placeholder.com/600x300?text=Upload+text+or+PDF+to+start", 
#                 use_column_width=True)

# if __name__ == "__main__":
#     main()


# ... (keep previous imports and setup code)

def main():
    """Main app controller with conversation continuity"""
    # Initialize session state
    if "characters" not in st.session_state:
        st.session_state.characters = []
    if "active_chats" not in st.session_state:
        st.session_state.active_chats = {}  # {character_name: [messages]}
    if "current_character" not in st.session_state:
        st.session_state.current_character = None

    # Sidebar - Character Management
    with st.sidebar:
        st.header("Character Manager")
        
        # File upload and character extraction (keep your existing code)
        setup_sidebar()
        
        # Character selection dropdown
        if st.session_state.characters:
            character_names = [char.name for char in st.session_state.characters]
            selected_char = st.selectbox(
                "Switch Character",
                character_names,
                index=character_names.index(st.session_state.current_character.name) 
                if st.session_state.current_character else 0
            )
            
            if st.button("Switch to Character"):
                st.session_state.current_character = next(
                    char for char in st.session_state.characters 
                    if char.name == selected_char
                )
                st.rerun()

            st.divider()
            st.write("Available Characters:")
            for char in st.session_state.characters:
                st.write(f"- {char.name}")

    # Main Chat Area
    st.title("Multi-Character Chat")
    
    if not st.session_state.characters:
        st.info("👈 Upload a book or paste text to extract characters")
        return

    if not st.session_state.current_character:
        st.session_state.current_character = st.session_state.characters[0]
        st.rerun()

    # Display current character info
    char = st.session_state.current_character
    st.subheader(f"Chatting with {char.name}")
    st.caption(f"Personality: {', '.join(char.traits)}")
    
    # Initialize chat history for this character if needed
    if char.name not in st.session_state.active_chats:
        st.session_state.active_chats[char.name] = [
            {"role": "assistant", "content": f"Hello! I'm {char.name}. How can I help you?"}
        ]

    # Display chat history
    for msg in st.session_state.active_chats[char.name]:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if prompt := st.chat_input(f"Message {char.name}..."):
        # Add user message to history
        st.session_state.active_chats[char.name].append(
            {"role": "user", "content": prompt}
        )
        st.chat_message("user").write(prompt)
        
        # Generate character response
        with st.spinner(f"{char.name} is thinking..."):
            try:
                context = f"""
                You are {char.name}, {char.description}.
                Personality: {', '.join(char.traits)}.
                Continue this conversation naturally:
                """
                
                # Get conversation history
                history = "\n".join(
                    f"{msg['role']}: {msg['content']}" 
                    for msg in st.session_state.active_chats[char.name]
                )
                
                response = model.generate_content([context, history])
                assistant_msg = response.text
                
                st.session_state.active_chats[char.name].append(
                    {"role": "assistant", "content": assistant_msg}
                )
                st.chat_message("assistant").write(assistant_msg)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")



if __name__ == "__main__":
    main()
