import os
import json
import streamlit as st
import chromadb
from dotenv import load_dotenv
import google.generativeai as gen_ai
from lib.character import Character
from lib.file_processor import extract_text_from_uploaded_file

# Load environment variables
load_dotenv()

# Configure Gemini-Pro
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-1.5-flash')

# Configure ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="character_chats")

# UI Configuration
st.set_page_config(page_title="AI Character Simulator", page_icon=":brain:", layout="wide")

def extract_characters(text: str) -> list[Character]:
    """Extract characters from text using Gemini"""
    if not text.strip():
        return []

    prompt = f"""
    Analyze this text and extract significant characters. For each character provide:
    - name (string)
    - description (string)
    - traits (list of strings)
    
    Return ONLY a valid JSON array of objects like:
    [
        {{
            "name": "Character Name",
            "description": "Character's role",
            "traits": ["trait1", "trait2"]
        }}
    ]
    
    Text to analyze:
    {text[:20000]}  # First 20k chars
    """

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip().strip('```json').strip('```').strip()
        characters_data = json.loads(json_str)
        
        return [
            Character(
                name=char.get('name', 'Unnamed'),
                description=char.get('description', 'No description'),
                traits=char.get('traits', [])
            ) for char in characters_data
        ]
        
    except Exception as e:
        st.error(f"Failed to extract characters. Error: {str(e)}")
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

def main():
    """Main app controller"""
    if "characters" not in st.session_state:
        st.session_state.characters = []
    if "all_conversations" not in st.session_state:
        st.session_state.all_conversations = {}
    if "current_character" not in st.session_state:
        st.session_state.current_character = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = "Ofgeha"

    with st.sidebar:
        st.header("User & Character Management")
        
        st.session_state.current_user = st.text_input(
            "Your Name", 
            value=st.session_state.current_user
        )

        setup_sidebar()

        if st.session_state.characters:
            character_names = [char.name for char in st.session_state.characters]
            
            selected_char = st.selectbox("Select Character", character_names, index=0)
            
            if st.button("Switch Character"):
                st.session_state.current_character = next(
                    char for char in st.session_state.characters if char.name == selected_char
                )
                st.rerun()

    if not st.session_state.current_character and st.session_state.characters:
        st.session_state.current_character = st.session_state.characters[0]
    
    if not st.session_state.current_character:
        st.info("👈 Upload a book or paste text to extract characters")
        return

    char_name = st.session_state.current_character.name
    user = st.session_state.current_user
    conversation_id = f"{char_name}-{user}"
    
    messages = collection.get(ids=[conversation_id])["metadatas"]
    if messages:
        messages = messages[0]["messages"]
    else:
        messages = [{"role": "assistant", "content": f"Hello {user}! I'm {char_name}. How can I help you?"}]
    
    for msg in messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input(f"Message {char_name}..."):
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(f"{user}: {prompt}")
        
        with st.spinner(f"{char_name} is thinking..."):
            try:
                char = st.session_state.current_character
                context = f"""
                You are {char.name}, {char.description}.
                Personality traits: {', '.join(char.traits)}.
                
                Conversation so far:
                {format_conversation_history(messages)}
                
                Respond naturally in character.
                """
                
                response = model.generate_content(context)
                assistant_msg = response.text
                
                messages.append({"role": "assistant", "content": assistant_msg})
                st.chat_message("assistant").write(assistant_msg)
                
                collection.add(
                    ids=[conversation_id],
                    metadatas=[{"messages": messages}]
                )
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def format_conversation_history(messages):
    """Format current conversation history"""
    return "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)

if __name__ == "__main__":
    main()
