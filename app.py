import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from lib.character import Character
from lib.file_processor import extract_text_from_uploaded_file
from ui import setup_page, create_sidebar, display_chat_header, display_conversation_history, display_user_input

# Load environment and configuration
load_dotenv()

# Configure Gemini-Pro
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-1.5-flash')

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

def main():
    """Main application logic"""
    # Initialize UI
    setup_page()
    
    # Initialize session state
    if "characters" not in st.session_state:
        st.session_state.characters = []
    if "all_conversations" not in st.session_state:
        st.session_state.all_conversations = {}
    if "current_character" not in st.session_state:
        st.session_state.current_character = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = "Ofgeha"

    # Create sidebar UI - pass the extract_characters function
    create_sidebar(st.session_state.characters, 
                  st.session_state.current_character,
                  extract_characters)

    # Main content area
    if not st.session_state.characters:
        st.info("Please upload a book or paste text to extract characters")
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

    # Display chat interface
    display_chat_header(st.session_state.current_character)
    display_conversation_history(st.session_state.all_conversations[char_name][st.session_state.current_user])

    # Handle user input
    if prompt := display_user_input(st.session_state.current_character):
        messages = st.session_state.all_conversations[char_name][st.session_state.current_user]
        
        # Add user message
        messages.append({"role": "user", "content": prompt, "user": st.session_state.current_user})
        
        # Generate response
        with st.spinner(f"{char_name} is thinking..."):
            try:
                char = st.session_state.current_character
                context = f"""
                You are {char.name}, {char.description}.
                Personality traits: {', '.join(char.traits)}.
                Current conversation with {st.session_state.current_user}:
                {format_conversation_history(messages)}
                Previous conversations with others:
                {format_other_conversations(char_name)}
                Respond naturally in character.
                """
                response = model.generate_content(context)
                messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def format_conversation_history(messages):
    """Format current conversation history"""
    return "\n".join(f"{msg.get('user', 'User')}: {msg['content']}" for msg in messages)

def format_other_conversations(char_name):
    """Format conversations with other users"""
    other_convos = []
    for user, messages in st.session_state.all_conversations[char_name].items():
        if user != st.session_state.current_user:
            other_convos.append(f"\nWith {user}:\n" + "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages[-3:]))
    return "\n".join(other_convos) if other_convos else "No previous conversations"

if __name__ == "__main__":
    main()