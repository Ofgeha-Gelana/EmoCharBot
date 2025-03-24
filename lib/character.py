import numpy as np
from typing import Dict, List

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