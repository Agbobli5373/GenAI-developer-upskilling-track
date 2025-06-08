"""
LLM Service Module for Chatbot
Handles LLM initialization and conversation chains with Google Gemini.
"""

from typing import Optional, Dict, Any
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM operations and conversation chains using Google Gemini."""
    
    def __init__(self, api_key: str = None, model_name: str = None, temperature: float = None):
        """
        Initialize LLM service with Google Gemini.
        
        Args:
            api_key: Google API key
            model_name: Model to use (e.g., 'gemini-1.5-flash')
            temperature: Sampling temperature for responses
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.temperature = temperature or float(os.getenv("TEMPERATURE", "0.7"))
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        self._llm = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the ChatGoogleGenerativeAI instance."""
        try:
            self._llm = ChatGoogleGenerativeAI(
                google_api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_output_tokens=int(os.getenv("MAX_TOKEN_LIMIT", "4000")) // 2,  # Reserve half for input
                convert_system_message_to_human=True  # Gemini compatibility
            )
            logger.info(f"LLM initialized with Gemini model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            raise
    
    def create_conversation_chain(self, memory: ConversationBufferMemory, 
                                custom_prompt: str = None) -> ConversationChain:
        """
        Create a conversation chain with memory.
        
        Args:
            memory: ConversationBufferMemory instance
            custom_prompt: Optional custom prompt template
            
        Returns:
            ConversationChain instance
        """
        # Default prompt template optimized for Gemini
        default_prompt = """You are a helpful AI assistant powered by Google Gemini with memory of our conversation. 
        You can remember what we've discussed previously and reference it in your responses.
        Be conversational, helpful, engaging, and provide accurate information.

        Previous conversation:
        {chat_history}

        Human: {input}
        Assistant:"""
        
        prompt_template = PromptTemplate(
            input_variables=["chat_history", "input"],
            template=custom_prompt or default_prompt
        )
        
        return ConversationChain(
            llm=self._llm,
            memory=memory,
            prompt=prompt_template,
            verbose=False
        )
    
    def process_message(self, chain: ConversationChain, message: str) -> str:
        """
        Process a user message through the conversation chain.
        
        Args:
            chain: ConversationChain instance
            message: User's input message
            
        Returns:
            AI's response
        """
        try:
            # Clean and validate input
            cleaned_message = self._clean_input(message)
            if not cleaned_message:
                return "I didn't receive any message. Could you please try again?"
            
            # Get response from chain
            response = chain.predict(input=cleaned_message)
            
            logger.info(f"Processed message successfully with Gemini. Input length: {len(cleaned_message)}")
            return response.strip()
            
        except Exception as e:
            error_msg = f"Error processing message with Gemini: {str(e)}"
            logger.error(error_msg)
            return "I apologize, but I encountered an error processing your message. Please try again."
    
    def _clean_input(self, message: str) -> str:
        """
        Clean and validate user input.
        
        Args:
            message: Raw user input
            
        Returns:
            Cleaned message
        """
        if not message or not isinstance(message, str):
            return ""
        
        # Remove excessive whitespace and limit length
        cleaned = message.strip()
        max_length = int(os.getenv("MAX_TOKEN_LIMIT", "4000")) // 4  # Conservative limit for Gemini
        
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            logger.warning(f"Input truncated to {max_length} characters for Gemini")
        
        return cleaned
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Gemini model configuration.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "model_provider": "Google Gemini",
            "temperature": self.temperature,
            "max_tokens": int(os.getenv("MAX_TOKEN_LIMIT", "4000")) // 2,
            "api_key_configured": bool(self.api_key)
        }
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Google Gemini API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Simple test call to Gemini
            test_response = self._llm.predict("Hello")
            return bool(test_response)
        except Exception as e:
            logger.error(f"Gemini connection validation failed: {e}")
            return False