"""
Streamlit Chatbot Application with Contextual Memory
Main application file for the memory-enabled chatbot.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

from llm_service import LLMService
from memory_manager import MemoryManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Gemini Contextual Memory Chatbot"),
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ChatbotApp:
    """Main chatbot application class."""
    
    def __init__(self):
        """Initialize the chatbot application."""
        self.initialize_session_state()
        self.setup_services()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'conversation_chain' not in st.session_state:
            st.session_state.conversation_chain = None
        
        if 'services_initialized' not in st.session_state:
            st.session_state.services_initialized = False
    
    def setup_services(self):
        """Initialize LLM and Memory services."""
        if not st.session_state.services_initialized:
            try:
                # Initialize services
                st.session_state.llm_service = LLMService()
                st.session_state.memory_manager = MemoryManager()
                
                # Create conversation chain
                memory = st.session_state.memory_manager.get_memory(st.session_state.session_id)
                st.session_state.conversation_chain = st.session_state.llm_service.create_conversation_chain(memory)
                
                st.session_state.services_initialized = True
                
            except Exception as e:
                st.error(f"Failed to initialize services: {e}")
                st.error("Please check your environment configuration.")
                st.stop()
    
    def render_sidebar(self):
        """Render the sidebar with controls and information."""
        with st.sidebar:
            st.title("🤖 Chatbot Controls")
            
            # Session information
            st.subheader("Session Info")
            st.write(f"**Session ID:** {st.session_state.session_id[:8]}...")
            st.write(f"**Messages:** {len(st.session_state.messages)}")
            
            # Memory statistics
            if st.session_state.services_initialized:
                memory_stats = st.session_state.memory_manager.get_memory_stats(st.session_state.session_id)
                st.write(f"**Memory Messages:** {memory_stats['total_messages']}")
            
            st.divider()
            
            # Controls
            st.subheader("Controls")
            
            if st.button("🗑️ Clear Conversation", type="secondary"):
                self.clear_conversation()
            
            if st.button("🔄 New Session", type="secondary"):
                self.new_session()
            
            st.divider()
            
            # Model information
            if st.session_state.services_initialized:
                st.subheader("Model Info")
                model_info = st.session_state.llm_service.get_model_info()
                st.write(f"**Model:** {model_info['model_name']}")
                st.write(f"**Temperature:** {model_info['temperature']}")
                st.write(f"**Max Tokens:** {model_info['max_tokens']}")
            
            st.divider()
            
            # Memory viewer
            if st.button("👁️ View Memory", type="secondary"):
                self.show_memory_viewer()
    
    def render_main_chat(self):
        """Render the main chat interface."""
        st.title(os.getenv("APP_TITLE", "Gemini Contextual Memory Chatbot"))
        st.write(os.getenv("APP_DESCRIPTION", "A chatbot powered by Google Gemini with short-term memory using LangChain"))
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "timestamp" in message:
                    st.caption(f"*{message['timestamp']}*")
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            self.handle_user_input(prompt)
    
    def handle_user_input(self, prompt: str):
        """
        Handle user input and generate response.
        
        Args:
            prompt: User's input message
        """
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {"role": "user", "content": prompt, "timestamp": timestamp}
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"*{timestamp}*")
        
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get response from LLM
                    response = st.session_state.llm_service.process_message(
                        st.session_state.conversation_chain, 
                        prompt
                    )
                    
                    # Display response
                    st.write(response)
                    response_timestamp = datetime.now().strftime("%H:%M:%S")
                    st.caption(f"*{response_timestamp}*")
                    
                    # Add AI response to chat
                    ai_message = {
                        "role": "assistant", 
                        "content": response, 
                        "timestamp": response_timestamp
                    }
                    st.session_state.messages.append(ai_message)
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg, 
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
    
    def clear_conversation(self):
        """Clear the current conversation."""
        st.session_state.messages = []
        if st.session_state.services_initialized:
            st.session_state.memory_manager.clear_session(st.session_state.session_id)
        st.rerun()
    
    def new_session(self):
        """Start a new session."""
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.services_initialized = False
        st.rerun()
    
    def show_memory_viewer(self):
        """Display memory viewer in a modal."""
        if st.session_state.services_initialized:
            history = st.session_state.memory_manager.get_conversation_history(st.session_state.session_id)
            if history:
                st.sidebar.text_area("Conversation Memory", history, height=200)
            else:
                st.sidebar.info("No conversation history yet.")
    
    def run(self):
        """Run the chatbot application."""
        self.render_sidebar()
        self.render_main_chat()


def main():
    """Main function to run the Streamlit app."""
    # Check for required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.error("Please create a .env file with your Google API key.")
        st.info("Get your API key from: https://aistudio.google.com/app/apikey")
        st.stop()
    
    # Initialize and run the app
    app = ChatbotApp()
    app.run()


if __name__ == "__main__":
    main()