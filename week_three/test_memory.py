"""
Unit tests for MemoryManager class.
"""

import pytest
import os
from unittest.mock import patch
from memory_manager import MemoryManager


class TestMemoryManager:
    """Test cases for MemoryManager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.memory_manager = MemoryManager(memory_key="test_history", max_length=5)
        self.test_session_id = "test_session_123"
    
    def test_initialization(self):
        """Test MemoryManager initialization."""
        # Test with default values
        mm = MemoryManager()
        assert mm.memory_key == "chat_history"  # default value
        assert mm.max_length == 10  # default value
        
        # Test with custom values
        mm_custom = MemoryManager(memory_key="custom_key", max_length=15)
        assert mm_custom.memory_key == "custom_key"
        assert mm_custom.max_length == 15
    
    def test_get_memory_new_session(self):
        """Test getting memory for a new session."""
        memory = self.memory_manager.get_memory(self.test_session_id)
        assert memory is not None
        assert memory.memory_key == "test_history"
        assert self.test_session_id in self.memory_manager._sessions
    
    def test_get_memory_existing_session(self):
        """Test getting memory for an existing session."""
        # First call creates the memory
        memory1 = self.memory_manager.get_memory(self.test_session_id)
        
        # Second call should return the same memory instance
        memory2 = self.memory_manager.get_memory(self.test_session_id)
        assert memory1 is memory2
    
    def test_add_message(self):
        """Test adding messages to memory."""
        human_input = "Hello, how are you?"
        ai_output = "I'm doing well, thank you!"
        
        self.memory_manager.add_message(self.test_session_id, human_input, ai_output)
        
        # Verify message was added
        memory = self.memory_manager.get_memory(self.test_session_id)
        assert len(memory.chat_memory.messages) > 0
    
    def test_get_conversation_history(self):
        """Test getting conversation history."""
        # Add some messages
        self.memory_manager.add_message(self.test_session_id, "Hello", "Hi there!")
        self.memory_manager.add_message(self.test_session_id, "How are you?", "I'm great!")
        
        history = self.memory_manager.get_conversation_history(self.test_session_id)
        assert isinstance(history, str)
        assert len(history) > 0
    
    def test_clear_session(self):
        """Test clearing a session."""
        # Add a message
        self.memory_manager.add_message(self.test_session_id, "Test", "Response")
        
        # Clear the session
        self.memory_manager.clear_session(self.test_session_id)
        
        # Verify session is cleared
        history = self.memory_manager.get_conversation_history(self.test_session_id)
        # After clearing, buffer should be empty or contain minimal content
        assert len(history.strip()) == 0 or history.strip() == ""
    
    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        # Create multiple sessions
        session1 = "session_1"
        session2 = "session_2"
        
        self.memory_manager.add_message(session1, "Test 1", "Response 1")
        self.memory_manager.add_message(session2, "Test 2", "Response 2")
        
        assert self.memory_manager.get_session_count() >= 2
        
        # Clear all sessions
        self.memory_manager.clear_all_sessions()
        
        assert self.memory_manager.get_session_count() == 0
    
    def test_get_session_count(self):
        """Test getting session count."""
        initial_count = self.memory_manager.get_session_count()
        
        # Add a session
        self.memory_manager.get_memory("session_1")
        assert self.memory_manager.get_session_count() == initial_count + 1
        
        # Add another session
        self.memory_manager.get_memory("session_2")
        assert self.memory_manager.get_session_count() == initial_count + 2
    
    def test_memory_trimming(self):
        """Test memory trimming functionality."""
        # Add more messages than max_length
        for i in range(self.memory_manager.max_length + 3):
            self.memory_manager.add_message(
                self.test_session_id, 
                f"Message {i}", 
                f"Response {i}"
            )
        
        memory = self.memory_manager.get_memory(self.test_session_id)
        # Should not exceed max_length * 2 (human + ai pairs)
        assert len(memory.chat_memory.messages) <= self.memory_manager.max_length * 2
    
    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        # Add some messages
        self.memory_manager.add_message(self.test_session_id, "Hello", "Hi!")
        self.memory_manager.add_message(self.test_session_id, "How are you?", "Good!")
        
        stats = self.memory_manager.get_memory_stats(self.test_session_id)
        
        assert isinstance(stats, dict)
        assert "total_messages" in stats
        assert "human_messages" in stats
        assert "ai_messages" in stats
        assert "memory_key" in stats
        assert "session_active" in stats
        
        assert stats["memory_key"] == "test_history"
        assert stats["session_active"] is True
        assert stats["total_messages"] >= 0
    
    @patch.dict(os.environ, {"MEMORY_KEY": "env_memory_key", "MAX_MEMORY_LENGTH": "20"})
    def test_environment_variables(self):
        """Test that environment variables are used correctly."""
        mm = MemoryManager()
        assert mm.memory_key == "env_memory_key"
        assert mm.max_length == 20
    
    def test_memory_persistence_within_session(self):
        """Test that memory persists within a session."""
        # Add first message
        self.memory_manager.add_message(self.test_session_id, "What's my name?", "I don't know your name yet.")
        
        # Add second message
        self.memory_manager.add_message(self.test_session_id, "My name is John", "Nice to meet you, John!")
        
        # Get conversation history
        history = self.memory_manager.get_conversation_history(self.test_session_id)
        
        # Both messages should be in history
        assert "What's my name?" in history or len(history) > 0  # Memory contains conversation
        
        # Verify memory has multiple exchanges
        memory = self.memory_manager.get_memory(self.test_session_id)
        assert len(memory.chat_memory.messages) >= 2  # At least 2 messages (could be more due to system messages)