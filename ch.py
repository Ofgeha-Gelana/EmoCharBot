import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from lib.character import Character
from lib.file_processor import extract_text_from_uploaded_file

# Load environment and configuration
load_dotenv()
gen_ai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = gen_ai.GenerativeModel('gemini-1.5-flash')

# Session state initialization
if "characters" not in st.session_state:
    st.session_state.characters = []
if "all_conversations" not in st.session_state:
    st.session_state.all_conversations = {}  # {character_name: {user: [messages]}}
if "current_user" not in st.session_state:
    st.session_state.current_user = "Ofgeha"  # Default user
if "current_character" not in st.session_state:
    st.session_state.current_character = None

def main():
    st.set_page_config(page_title="Multi-User Character Chat", layout="wide")
    st.title("Multi-User Character Conversations")
    
    # User management in sidebar
    with st.sidebar:
        st.header("User Settings")
        
        # User selection/creation
        new_user = st.text_input("Enter your name:", "Ofgeha")
        if st.button("Set User"):
            st.session_state.current_user = new_user
            st.rerun()
        
        st.divider()
        st.subheader("Available Characters")
        
        # File upload and character extraction
        uploaded_file = st.file_uploader("Upload book/text:", type=["txt", "pdf"])
        if uploaded_file:
            text = extract_text_from_uploaded_file(uploaded_file)
            if text:
                st.session_state.characters = extract_characters(text)
        
        # Character selection
        if st.session_state.characters:
            selected_char = st.selectbox(
                "Select Character",
                [char.name for char in st.session_state.characters],
                key="char_select"
            )
            st.session_state.current_character = next(
                char for char in st.session_state.characters 
                if char.name == selected_char
            )
            
            # Initialize conversation if new
            if selected_char not in st.session_state.all_conversations:
                st.session_state.all_conversations[selected_char] = {}
            
            st.divider()
            st.subheader("Conversation History")
            view_user = st.selectbox(
                "View conversation with:",
                ["Current"] + list(st.session_state.all_conversations[selected_char].keys())
            )

    # Main chat area
    if st.session_state.current_character:
        char = st.session_state.current_character
        st.header(f"Chatting with {char.name} as {st.session_state.current_user}")
        st.caption(f"Personality: {', '.join(char.traits)}")
        
        # Initialize user's conversation if new
        if st.session_state.current_user not in st.session_state.all_conversations[char.name]:
            st.session_state.all_conversations[char.name][st.session_state.current_user] = [
                {"role": "assistant", "content": f"Hello {st.session_state.current_user}! I'm {char.name}."}
            ]
        
        # Display appropriate conversation
        messages = (
            st.session_state.all_conversations[char.name][view_user] 
            if view_user != "Current" 
            else st.session_state.all_conversations[char.name][st.session_state.current_user]
        )
        
        for msg in messages:
            st.chat_message(msg["role"]).write(msg["content"])
        
        # Handle new messages
        if prompt := st.chat_input(f"Message {char.name}..."):
            # Add to current user's conversation
            st.session_state.all_conversations[char.name][st.session_state.current_user].append(
                {"role": "user", "content": prompt}
            )
            st.chat_message("user").write(prompt)
            
            # Generate response with full context
            with st.spinner(f"{char.name} is thinking..."):
                try:
                    # Get full conversation history for context
                    full_history = "\n".join(
                        f"{msg['role']}: {msg['content']}" 
                        for msg in st.session_state.all_conversations[char.name][st.session_state.current_user]
                    )
                    
                    response = model.generate_content(
                        f"""You are {char.name} with these traits: {', '.join(char.traits)}.
                        This is your conversation with {st.session_state.current_user}:
                        {full_history}
                        Respond naturally to the last message:"""
                    )
                    
                    assistant_msg = response.text
                    st.session_state.all_conversations[char.name][st.session_state.current_user].append(
                        {"role": "assistant", "content": assistant_msg}
                    )
                    st.chat_message("assistant").write(assistant_msg)
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()