# AI Character Simulator 🎭

Welcome to the **AI Character Simulator** project, a powerful and interactive tool that allows you to engage in conversations with characters extracted from any text, such as books, stories, or documents! This project uses Streamlit for the frontend, Google's Gemini-Pro for AI-driven character generation, and ChromaDB for efficient conversation storage.

---

## 🚀 **Project Overview**

The **AI Character Simulator** enables users to:
- Extract and interact with characters from any text (e.g., books, stories, documents).
- Store conversations with each character using ChromaDB, ensuring data persistence.
- Engage in dynamic, AI-powered chats with characters, allowing for fun and meaningful conversations.
  
---

## 🧑‍💻 **Technologies Used**

- **Streamlit**: Framework for creating interactive web applications.
- **Google Gemini-Pro**: AI model to generate responses based on character traits and personality.
- **ChromaDB**: Database for managing and storing conversation history.
- **Python**: Core programming language used in the backend.

---

## 🏗 **Setup Instructions**

### Prerequisites

1. **Python 3.12+**  
2. **Streamlit**: Used for the web app interface.
3. **Google API Key**: For using Google's Gemini-Pro AI model.
4. **ChromaDB**: For persistent storage of conversation data.

### Steps to Run the Project

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Ofgeha-Gelana/EmoCharBot.git
    cd EmoCharBot
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
   - Create a `.env` file in the root directory of the project.
   - Add your **Google API Key** to the `.env` file:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

5. **Run the app**:
    ```bash
    streamlit run dp.py
    ```

    This will start a local Streamlit app accessible at `http://localhost:8501`.

---

## 🌟 **Features**

- **Character Extraction**: 
   - Upload a text document or paste text directly into the app.
   - The AI will analyze the text and extract key characters with descriptions and traits.
   
- **Character Interaction**:
   - Choose a character to chat with based on extracted data.
   - Chat naturally with characters, where responses are AI-generated based on the character’s traits and context.

- **Conversation Persistence**:
   - Conversations are stored in ChromaDB, which allows you to refer to past conversations and continue chatting seamlessly.
   
- **Character Management**:
   - Easily switch between different characters and manage multiple conversations at once.
   
---

## ⚙️ **How to Use**

1. **Step 1: Extract Characters**
    - Paste the text or upload a file containing the story or content.
    - The AI will analyze the text and extract characters along with their descriptions and traits.

2. **Step 2: Select a Character**
    - Choose one of the extracted characters from a list.
    - The character's description and traits will be displayed.

3. **Step 3: Start Chatting**
    - Begin chatting with the selected character. The AI will respond in the character's persona, taking into account their traits and role in the story.
    
4. **Step 4: View Conversation History**
    - Conversations with each character are stored and can be accessed later.
    - You can continue previous conversations or start new ones at any time.

---

## 📦 **Project Structure**

