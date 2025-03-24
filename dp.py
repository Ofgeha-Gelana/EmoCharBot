import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import json
from typing import Dict, List, Tuple
import numpy as np

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="AI Character Simulator",
    page_icon=":brain:",  # Favicon emoji
    layout="wide",  # Wider layout for our dashboard
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-1.5-flash')

# --- Psi Theory Implementation ---
class PsiEmotionModel:
    """Implements Dorner's Psi Theory for emotional adaptation"""
    
    def __init__(self, initial_params: Dict[str, float] = None):
        # Default parameters (neutral state)
        self.params = {
            'valence': 0.5,        # -1 (aversive) to 1 (appetitive)
            'arousal': 0.5,        # 0 (low) to 1 (high)
            'selection_threshold': 0.5,  # 0 (flexible) to 1 (rigid)
            'resolution_level': 0.7,    # 0 (broad) to 1 (detailed)
            'goal_directedness': 0.6,   # 0 (adaptive) to 1 (focused)
            'securing_rate': 0.4        # 0 (rare checks) to 1 (frequent checks)
        }
        
        if initial_params:
            self.params.update(initial_params)
        
        self.emotion_state = "Neutral"
        self.emotion_history = []
    
    def update_from_interaction(self, user_input: str, sentiment: float):
        """Update parameters based on user input and sentiment"""
        
        # Adjust based on sentiment analysis
        self.params['valence'] = np.clip(self.params['valence'] + sentiment * 0.1, 0, 1)
        
        # Increase arousal for emotional inputs
        emotional_intensity = abs(sentiment)
        self.params['arousal'] = np.clip(self.params['arousal'] + emotional_intensity * 0.1, 0, 1)
        
        # Specific triggers from user input
        user_input_lower = user_input.lower()
        
        # Anger triggers
        if any(word in user_input_lower for word in ["angry", "mad", "hate", "annoy"]):
            self.params['selection_threshold'] = min(1.0, self.params['selection_threshold'] + 0.15)
            self.params['resolution_level'] = max(0.1, self.params['resolution_level'] - 0.1)
            self.params['arousal'] = min(1.0, self.params['arousal'] + 0.2)
        
        # Sadness triggers
        elif any(word in user_input_lower for word in ["sad", "depress", "cry", "lonely"]):
            self.params['arousal'] = max(0.0, self.params['arousal'] - 0.15)
            self.params['goal_directedness'] = max(0.0, self.params['goal_directedness'] - 0.1)
        
        # Joy triggers
        elif any(word in user_input_lower for word in ["happy", "joy", "excite", "love"]):
            self.params['valence'] = min(1.0, self.params['valence'] + 0.15)
            self.params['arousal'] = min(1.0, self.params['arousal'] + 0.1)
            self.params['securing_rate'] = max(0.0, self.params['securing_rate'] - 0.05)
        
        self._calculate_emotion_state()
        self.emotion_history.append((self.emotion_state, self.params.copy()))
    
    def _calculate_emotion_state(self):
        """Determine current emotional state based on parameters"""
        valence = self.params['valence']
        arousal = self.params['arousal']
        sel_thresh = self.params['selection_threshold']
        
        if valence < 0.3 and arousal > 0.7 and sel_thresh > 0.7:
            self.emotion_state = "Anger"
        elif valence < 0.4 and arousal < 0.4:
            self.emotion_state = "Sadness"
        elif valence > 0.7 and arousal > 0.6:
            self.emotion_state = "Joy"
        elif valence > 0.7 and arousal < 0.4:
            self.emotion_state = "Bliss"
        elif sel_thresh < 0.3 and self.params['goal_directedness'] < 0.4:
            self.emotion_state = "Confusion"
        else:
            self.emotion_state = "Neutral"

# --- Character Management ---
class Character:
    """Represents a simulated character with personality and emotional model"""
    
    def __init__(self, name: str, description: str, traits: Dict):
        self.name = name
        self.description = description
        self.traits = traits
        self.psi_model = PsiEmotionModel(self._map_traits_to_psi())
        self.memory = []  # Stores conversation history
    
    def _map_traits_to_psi(self) -> Dict[str, float]:
        """Map personality traits to initial Psi parameters"""
        params = {}
        
        # Example mappings - these would be more sophisticated in production
        if "aggressive" in self.traits:
            params['selection_threshold'] = 0.8
            params['arousal'] = 0.7
        if "optimistic" in self.traits:
            params['valence'] = 0.7
        if "detailed" in self.traits:
            params['resolution_level'] = 0.9
        
        return params

# --- Text Processing Functions ---
def extract_characters(text: str) -> List[Character]:
    """Use Gemini to extract characters from text"""
    prompt = f"""
    Analyze the following text and extract significant characters with:
    - Name
    - Description/role
    - Key personality traits (e.g., kind, aggressive, witty)
    - Typical emotional tendencies
    
    Return as a JSON list where each item has:
    name, description, traits (list), emotional_tendencies
    
    Text: {text[:10000]}  # Limiting for demo
    """
    
    try:
        response = model.generate_content(prompt)
        characters_data = json.loads(response.text)
        return [Character(
            name=char['name'],
            description=char['description'],
            traits=char['traits']
        ) for char in characters_data]
    except Exception as e:
        st.error(f"Error extracting characters: {e}")
        return []

# --- UI Helpers ---
def display_psi_parameters(params: Dict[str, float], emotion: str):
    """Display the current Psi parameters visually"""
    st.sidebar.subheader("Current Emotional State")
    st.sidebar.markdown(f"**{emotion}**")
    
    st.sidebar.subheader("Psi Parameters")
    for param, value in params.items():
        st.sidebar.progress(value, text=f"{param.replace('_', ' ').title()}: {value:.2f}")

# --- Session State Initialization ---
if "characters" not in st.session_state:
    st.session_state.characters = []
if "selected_character" not in st.session_state:
    st.session_state.selected_character = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Main App Interface ---
st.title("📚 AI Character Simulator with Emotional Adaptation")

# Sidebar for character selection and parameters
with st.sidebar:
    st.header("Character Setup")
    
    # Text input or upload for book
    input_method = st.radio("Input method:", ("Paste text", "Upload file"))
    
    if input_method == "Paste text":
        book_text = st.text_area("Paste book text:", height=200)
    else:
        uploaded_file = st.file_uploader("Upload book/text file:", type=["txt", "pdf"])
        if uploaded_file:
            book_text = uploaded_file.read().decode("utf-8")
    
    if st.button("Extract Characters") and book_text:
        st.session_state.characters = extract_characters(book_text)
    
    if st.session_state.characters:
        character_names = [char.name for char in st.session_state.characters]
        selected = st.selectbox("Select a character:", character_names)
        st.session_state.selected_character = next(
            char for char in st.session_state.characters if char.name == selected
        )
        
        # Display character info
        st.subheader("Character Info")
        char = st.session_state.selected_character
        st.markdown(f"**Name:** {char.name}")
        st.markdown(f"**Description:** {char.description}")
        st.markdown("**Traits:** " + ", ".join(char.traits))
        
        # Display Psi parameters if character selected
        if st.session_state.selected_character:
            display_psi_parameters(
                char.psi_model.params,
                char.psi_model.emotion_state
            )

# Main chat area
if st.session_state.selected_character:
    char = st.session_state.selected_character
    
    st.header(f"Chatting with {char.name}")
    st.caption(f"{char.description}")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        role = "assistant" if msg["role"] == "character" else "user"
        with st.chat_message(role):
            st.markdown(msg["content"])
            if role == "assistant" and msg.get("emotion"):
                st.caption(f"*[{msg['emotion']}]*")
    
    # User input
    user_input = st.chat_input(f"Talk to {char.name}...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate character response with emotional context
        prompt = f"""
        You are {char.name}, a character with these traits: {', '.join(char.traits)}.
        Your current emotional state is: {char.psi_model.emotion_state}.
        
        Respond to the user naturally while staying in character.
        User: {user_input}
        {char.name}:
        """
        
        try:
            response = model.generate_content(prompt)
            char_response = response.text
            
            # Add to character's memory
            char.memory.append({
                "user_input": user_input,
                "response": char_response,
                "emotion": char.psi_model.emotion_state,
                "psi_params": char.psi_model.params.copy()
            })
            
            # Add to session chat history
            st.session_state.chat_history.append({
                "role": "character",
                "content": char_response,
                "emotion": char.psi_model.emotion_state
            })
            
            # Display character response
            with st.chat_message("assistant"):
                st.markdown(char_response)
                st.caption(f"*[{char.psi_model.emotion_state}]*")
            
            # Simple sentiment analysis (in production would use proper NLP)
            sentiment = 0.1  # Neutral baseline
            if any(word in user_input.lower() for word in ["happy", "great", "love"]):
                sentiment = 0.5
            elif any(word in user_input.lower() for word in ["sad", "bad", "hate"]):
                sentiment = -0.5
            
            # Update emotional model
            char.psi_model.update_from_interaction(user_input, sentiment)
            
        except Exception as e:
            st.error(f"Error generating response: {e}")

else:
    st.info("Please upload or paste text and extract characters to begin chatting.")
    st.image("https://via.placeholder.com/600x300?text=Upload+a+book+to+start", use_column_width=True)

# --- Memory Feature (Bonus) ---
if st.session_state.selected_character and st.session_state.chat_history:
    st.sidebar.header("Memory Features")
    memory_query = st.sidebar.text_input("Ask about past interactions:")
    
    if memory_query:
        # Simple memory lookup (would be more sophisticated in production)
        char = st.session_state.selected_character
        relevant_memories = [
            m for m in char.memory 
            if memory_query.lower() in m["user_input"].lower() or 
               memory_query.lower() in m["response"].lower()
        ]
        
        if relevant_memories:
            st.sidebar.subheader("Relevant Memories")
            for mem in relevant_memories[:3]:  # Limit display
                st.sidebar.text(f"User: {mem['user_input'][:50]}...")
                st.sidebar.text(f"{char.name}: {mem['response'][:50]}...")
                st.sidebar.caption(f"Emotion: {mem['emotion']}")
                st.sidebar.divider()
        else:
            st.sidebar.info("No memories found matching that query.")