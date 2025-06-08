"""
Memory Manager Module for Chatbot
Handles conversation memory and session management.
"""

from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
import os


class MemoryManager:
    """Manages conversation memory for the chatbot."""
    
    def __init__(self, memory_key: str = None, max_length: int = None):
        """
        Initialize memory manager.
        
        Args:
            memory_key: Key for storing conversation history
            max_length: Maximum number of exchanges to remember
        """
        self.memory_key = memory_key or os.getenv("MEMORY_KEY", "chat_history")
        self.max_length = max_length or int(os.getenv("MAX_MEMORY_LENGTH", "10"))
        self._sessions: Dict[str, ConversationBufferMemory] = {}
    
    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        Get or create memory for a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            ConversationBufferMemory instance for the session
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationBufferMemory(
                memory_key=self.memory_key,
                return_messages=True,
                max_token_limit=int(os.getenv("MAX_TOKEN_LIMIT", "4000"))
            )
        
        return self._sessions[session_id]
    
    def add_message(self, session_id: str, human_input: str, ai_output: str) -> None:
        """
        Add a conversation exchange to memory.
        
        Args:
            session_id: Session identifier
            human_input: User's message
            ai_output: AI's response
        """
        memory = self.get_memory(session_id)
        memory.save_context(
            {"input": human_input},
            {"output": ai_output}
        )
        
        # Trim memory if it exceeds max length
        self._trim_memory(session_id)
    
    def get_conversation_history(self, session_id: str) -> str:
        """
        Get formatted conversation history.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted conversation history as string
        """
        memory = self.get_memory(session_id)
        return memory.buffer
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear memory for a specific session.
        
        Args:
            session_id: Session identifier to clear
        """
        if session_id in self._sessions:
            self._sessions[session_id].clear()
    
    def clear_all_sessions(self) -> None:
        """Clear all session memories."""
        for session_id in self._sessions:
            self._sessions[session_id].clear()
        self._sessions.clear()
    
    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)
    
    def _trim_memory(self, session_id: str) -> None:
        """
        Trim memory to stay within max_length limit.
        
        Args:
            session_id: Session identifier
        """
        memory = self.get_memory(session_id)
        messages = memory.chat_memory.messages
        
        # Keep only the last max_length * 2 messages (pairs of human/ai)
        if len(messages) > self.max_length * 2:
            memory.chat_memory.messages = messages[-(self.max_length * 2):]
    
    def get_memory_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing memory statistics
        """
        memory = self.get_memory(session_id)
        messages = memory.chat_memory.messages
        
        return {
            "total_messages": len(messages),
            "human_messages": len([m for m in messages if hasattr(m, 'content') and 'Human:' in str(m)]),
            "ai_messages": len([m for m in messages if hasattr(m, 'content') and 'AI:' in str(m)]),
            "memory_key": self.memory_key,
            "session_active": session_id in self._sessions
        }