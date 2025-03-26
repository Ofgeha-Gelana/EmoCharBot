import json
from lib.character import Character
import google.generativeai as gen_ai
import streamlit as st


def initialize_session_state():
    """Initialize all required session state variables"""
    if "characters" not in st.session_state:
        st.session_state.characters = []
    if "current_character" not in st.session_state:
        st.session_state.current_character = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = "Guest"

def extract_characters(text: str) -> list[Character]:
    """
    Extract characters from text using AI with robust error handling
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        List[Character]: List of extracted characters
        
    Raises:
        ValueError: If text parsing fails
    """
    if not text.strip():
        st.warning("Please provide text with content")
        return []

    try:
        # Structured prompt with clear output format
        prompt = f"""
        ANALYZE THIS TEXT AND EXTRACT CHARACTERS:
        
        Instructions:
        1. Identify all significant characters
        2. For each provide:
           - name (string)
           - description (string)
           - traits (list of 3-5 strings)
        3. Return ONLY valid JSON
        
        Required JSON format:
        {{
            "characters": [
                {{
                    "name": "Character Name",
                    "description": "1-2 sentence description",
                    "traits": ["trait1", "trait2", "trait3"]
                }}
            ]
        }}
        
        Text to analyze (first 20k chars):
        {text[:20000]}
        """
        
        # Generate response with stricter configuration
        response = gen_ai.generate_content(
            contents=[prompt],
            generation_config={
                "temperature": 0.3,  # More deterministic
                "top_p": 0.7,
                "max_output_tokens": 2000
            }
        )
        
        # Parse with multiple fallback strategies
        try:
            # First try direct parse
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Try extracting from markdown code block
            json_str = response.text.strip()
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            data = json.loads(json_str)
        
        # Validate response structure
        if "characters" not in data or not isinstance(data["characters"], list):
            raise ValueError("Invalid character data format")
            
        # Create Character objects with validation
        characters = []
        for char_data in data["characters"]:
            try:
                characters.append(Character(
                    name=char_data["name"].strip(),
                    description=char_data["description"].strip(),
                    traits=[t.strip() for t in char_data["traits"]]
                ))
            except KeyError as e:
                st.warning(f"Skipping invalid character: Missing {str(e)}")
                continue
                
        if not characters:
            raise ValueError("No valid characters found")
            
        return characters
        
    except Exception as e:
        st.error("Character extraction failed")
        st.json({"error": str(e), "raw_response": response.text if 'response' in locals() else None})
        return []