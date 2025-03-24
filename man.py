



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


def main():
    """Main app controller with user-specific conversation tracking"""
    # Initialize session state
    if "characters" not in st.session_state:
        st.session_state.characters = []
    if "all_conversations" not in st.session_state:
        st.session_state.all_conversations = {}  # Format: {character_name: {user: [messages]}}
    if "current_character" not in st.session_state:
        st.session_state.current_character = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = "Ofgeha"  # Default user

    # User management in sidebar
    with st.sidebar:
        st.header("User & Character Management")
        
        # User selection
        st.session_state.current_user = st.text_input(
            "Your Name", 
            value=st.session_state.current_user,
            help="Enter your name to continue or start a new conversation"
        )
        
        # File upload and character extraction
        setup_sidebar()
        
        # Character selection
        if st.session_state.characters:
            character_names = [char.name for char in st.session_state.characters]
            selected_char = st.selectbox(
                "Select Character",
                character_names,
                index=character_names.index(st.session_state.current_character.name) 
                if st.session_state.current_character else 0
            )
            
            if st.button("Switch Character"):
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
    st.title(f"💬 {st.session_state.current_user}'s Conversation")
    
    if not st.session_state.characters:
        st.info("👈 Upload a book or paste text to extract characters")
        return

    if not st.session_state.current_character:
        st.session_state.current_character = st.session_state.characters[0]
        st.rerun()

    # Initialize conversation tracking
    char_name = st.session_state.current_character.name
    if char_name not in st.session_state.all_conversations:
        st.session_state.all_conversations[char_name] = {}
    
    # Get or create conversation for current user
    if st.session_state.current_user not in st.session_state.all_conversations[char_name]:
        st.session_state.all_conversations[char_name][st.session_state.current_user] = [
            {"role": "assistant", "content": f"Hello {st.session_state.current_user}! I'm {char_name}. How can I help you?"}
        ]

    # Display conversation history
    messages = st.session_state.all_conversations[char_name][st.session_state.current_user]
    for msg in messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if prompt := st.chat_input(f"Message {char_name}..."):
        # Add user message to history
        messages.append({"role": "user", "content": prompt, "user": st.session_state.current_user})
        st.chat_message("user").write(f"{st.session_state.current_user}: {prompt}")
        
        # Generate character response
        with st.spinner(f"{char_name} is thinking..."):
            try:
                char = st.session_state.current_character
                
                # Build context with character info and full conversation history
                context = f"""
                You are {char.name}, {char.description}.
                Personality traits: {', '.join(char.traits)}.
                
                Current conversation with {st.session_state.current_user}:
                {format_conversation_history(messages)}
                
                Previous conversations with others:
                {format_other_conversations(char_name)}
                
                Respond naturally in character, remembering you've spoken with others before.
                """
                
                response = model.generate_content(context)
                assistant_msg = response.text
                
                messages.append({"role": "assistant", "content": assistant_msg})
                st.chat_message("assistant").write(assistant_msg)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def format_conversation_history(messages):
    """Format current conversation history"""
    return "\n".join(
        f"{msg.get('user', 'User')}: {msg['content']}" 
        for msg in messages 
        if msg['role'] != "system"
    )

def format_other_conversations(char_name):
    """Format conversations with other users"""
    other_convos = []
    for user, messages in st.session_state.all_conversations[char_name].items():
        if user != st.session_state.current_user:
            convo = f"\nConversation with {user}:\n"
            convo += "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages[-3:])  # Show last 3 messages
            other_convos.append(convo)
    return "\n".join(other_convos) if other_convos else "No previous conversations with others"

if __name__ == "__main__":
    main()

