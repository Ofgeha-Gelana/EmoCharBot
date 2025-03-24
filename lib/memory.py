class MemorySystem:
    """Handles conversation memory and recall"""
    
    def __init__(self):
        self.memories = []
    
    def add_memory(self, user_input: str, response: str, emotion: str, params: dict):
        """Store a conversation memory"""
        self.memories.append({
            'user_input': user_input,
            'response': response,
            'emotion': emotion,
            'params': params.copy()
        })
    
    def query_memory(self, query: str) -> list:
        """Search for relevant memories"""
        return [m for m in self.memories 
               if query.lower() in m['user_input'].lower() or 
               query.lower() in m['response'].lower()]