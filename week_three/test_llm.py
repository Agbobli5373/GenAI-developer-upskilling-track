"""
Unit tests for LLMService class with Google Gemini.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from langchain.memory import ConversationBufferMemory
from llm_service import LLMService


class TestLLMService:
    """Test cases for LLMService with Gemini."""
    
    def setup_method(self):
        """Setup test environment."""
        # Mock API key for testing
        self.test_api_key = "test_google_api_key_123"
        self.test_model = "gemini-pro"
        self.test_temperature = 0.7
    
    def test_initialization_with_params(self):
        """Test LLMService initialization with parameters."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            service = LLMService(
                api_key=self.test_api_key,
                model_name=self.test_model,
                temperature=self.test_temperature
            )
            
            assert service.api_key == self.test_api_key
            assert service.model_name == self.test_model
            assert service.temperature == self.test_temperature
            mock_chat.assert_called_once()
    
    @patch.dict(os.environ, {
        "GOOGLE_API_KEY": "env_api_key",
        "MODEL_NAME": "gemini-1.5-flash",
        "TEMPERATURE": "0.8"
    })
    def test_initialization_with_env_vars(self):
        """Test LLMService initialization with environment variables."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            service = LLMService()
            
            assert service.api_key == "env_api_key"
            assert service.model_name == "gemini-1.5-flash"
            assert service.temperature == 0.8
            mock_chat.assert_called_once()
    
    def test_initialization_without_api_key(self):
        """Test LLMService initialization without API key raises error."""
        with pytest.raises(ValueError, match="Google API key is required"):
            LLMService(api_key=None)
    
    def test_create_conversation_chain(self):
        """Test creating conversation chain."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            memory = ConversationBufferMemory(return_messages=True)
            
            chain = service.create_conversation_chain(memory)
            
            assert chain is not None
            assert chain.memory == memory
            assert "Gemini" in chain.prompt.template
    
    def test_create_conversation_chain_with_custom_prompt(self):
        """Test creating conversation chain with custom prompt."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            memory = ConversationBufferMemory(return_messages=True)
            custom_prompt = "Custom prompt: {chat_history}\nUser: {input}\nBot:"
            
            chain = service.create_conversation_chain(memory, custom_prompt)
            
            assert chain is not None
            assert custom_prompt in chain.prompt.template
    
    def test_clean_input_normal_message(self):
        """Test cleaning normal input message."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            
            test_message = "  Hello, how are you?  "
            cleaned = service._clean_input(test_message)
            
            assert cleaned == "Hello, how are you?"
    
    def test_clean_input_empty_message(self):
        """Test cleaning empty input message."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            
            assert service._clean_input("") == ""
            assert service._clean_input("   ") == ""
            assert service._clean_input(None) == ""
    
    def test_clean_input_long_message(self):
        """Test cleaning very long input message."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            
            # Create a very long message
            long_message = "x" * 2000
            cleaned = service._clean_input(long_message)
            
            # Should be truncated
            assert len(cleaned) < len(long_message)
            assert cleaned.endswith("...")
    
    def test_process_message_success(self):
        """Test successful message processing."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            # Mock the chain's predict method
            mock_chain = MagicMock()
            mock_chain.predict.return_value = "Test response from Gemini"
            
            service = LLMService(api_key=self.test_api_key)
            
            result = service.process_message(mock_chain, "Test message")
            
            assert result == "Test response from Gemini"
            mock_chain.predict.assert_called_once_with(input="Test message")
    
    def test_process_message_empty_input(self):
        """Test processing empty input message."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            mock_chain = MagicMock()
            
            result = service.process_message(mock_chain, "")
            
            assert "didn't receive any message" in result
            mock_chain.predict.assert_not_called()
    
    def test_process_message_with_error(self):
        """Test message processing with error."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(api_key=self.test_api_key)
            
            mock_chain = MagicMock()
            mock_chain.predict.side_effect = Exception("Gemini API error")
            
            result = service.process_message(mock_chain, "Test message")
            
            assert "Error processing message with Gemini" in result
            assert "apologize" in result
    
    def test_get_model_info(self):
        """Test getting model information."""
        with patch('llm_service.ChatGoogleGenerativeAI'):
            service = LLMService(
                api_key=self.test_api_key,
                model_name=self.test_model,
                temperature=self.test_temperature
            )
            
            info = service.get_model_info()
            
            assert info["model_name"] == self.test_model
            assert info["model_provider"] == "Google Gemini"
            assert info["temperature"] == self.test_temperature
            assert info["api_key_configured"] is True
            assert "max_tokens" in info
    
    def test_validate_connection_success(self):
        """Test successful connection validation."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.predict.return_value = "Hello from Gemini"
            mock_chat.return_value = mock_llm
            
            service = LLMService(api_key=self.test_api_key)
            
            result = service.validate_connection()
            
            assert result is True
            mock_llm.predict.assert_called_once_with("Hello")
    
    def test_validate_connection_failure(self):
        """Test connection validation failure."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.predict.side_effect = Exception("Connection failed")
            mock_chat.return_value = mock_llm
            
            service = LLMService(api_key=self.test_api_key)
            
            result = service.validate_connection()
            
            assert result is False
    
    @patch.dict(os.environ, {"MAX_TOKEN_LIMIT": "8000"})
    def test_token_limit_configuration(self):
        """Test token limit configuration from environment."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            service = LLMService(api_key=self.test_api_key)
            
            info = service.get_model_info()
            assert info["max_tokens"] == 4000  # Half of MAX_TOKEN_LIMIT
    
    def test_gemini_specific_initialization(self):
        """Test Gemini-specific initialization parameters."""
        with patch('llm_service.ChatGoogleGenerativeAI') as mock_chat:
            service = LLMService(api_key=self.test_api_key)
            
            # Verify ChatGoogleGenerativeAI was called with correct parameters
            call_args = mock_chat.call_args
            assert call_args[1]['google_api_key'] == self.test_api_key
            assert call_args[1]['model'] == 'gemini-pro'
            assert call_args[1]['convert_system_message_to_human'] is True


class TestLLMServiceIntegration:
    """Integration tests for LLMService (require actual API key)."""
    
    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires Google API key")
    def test_real_gemini_connection(self):
        """Test real connection to Gemini (requires API key)."""
        service = LLMService()
        assert service.validate_connection() is True
    
    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires Google API key")
    def test_real_conversation_chain(self):
        """Test real conversation chain with Gemini."""
        service = LLMService()
        memory = ConversationBufferMemory(return_messages=True)
        chain = service.create_conversation_chain(memory)
        
        response = service.process_message(chain, "Hello, can you remember this conversation?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "error" not in response.lower()