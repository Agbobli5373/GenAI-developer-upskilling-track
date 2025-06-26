#!/usr/bin/env python3
import streamlit as st
import os
from agent import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_models():
    """Initialize both the tool-enabled agent and the generic LLM."""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
        st.stop()
    
    try:
        # Initialize tool-enabled agent
        agent = create_agent()
        
        # Initialize generic LLM for general questions
        generic_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            api_key=SecretStr(os.getenv("GOOGLE_API_KEY") or "")
        )
        
        return agent, generic_llm
    except Exception as e:
        st.error(f"❌ Error initializing models: {e}")
        st.stop()

def is_tool_query(query):
    """Determine if a query likely needs tool usage."""
    tool_keywords = [
        # Calculator keywords
        'calculate', 'compute', 'math', 'plus', 'minus', 'multiply', 'divide',
        'add', 'subtract', 'square root', 'sqrt', 'sin', 'cos', 'tan', 
        'logarithm', 'log', 'exponential', 'power', 'equation', 'solve',
        '+', '-', '*', '/', '=', '^', '%',
        
        # Weather keywords
        'weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy',
        'humidity', 'wind', 'storm', 'hot', 'cold', 'degrees', 'celsius',
        'fahrenheit', 'climate', 'meteorology'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in tool_keywords)

def main():
    """Main Streamlit application."""
    
    # Sidebar
    st.sidebar.title("🤖 Gemini AI Assistant")
    st.sidebar.markdown("---")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Select Mode:",
        ["🤖 Auto Mode (Recommended)", "🛠️ Tool Mode", "💭 Chat Mode"],
        help="Auto Mode automatically detects if you need tools or general chat"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Available Tools:")
    st.sidebar.markdown("📊 **Calculator** - Math operations")
    st.sidebar.markdown("🌤️ **Weather** - Current weather info")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Examples:")
    with st.sidebar.expander("Calculator Examples"):
        st.markdown("""
        - "Calculate 15 * 23"
        - "What is the square root of 144?"
        - "Solve sin(30) + cos(60)"
        """)
    
    with st.sidebar.expander("Weather Examples"):
        st.markdown("""
        - "What's the weather in London?"
        - "Temperature in Tokyo"
        - "Weather forecast for New York"
        """)
    
    with st.sidebar.expander("General Questions"):
        st.markdown("""
        - "Explain quantum computing"
        - "Write a poem about AI"
        - "Help me plan a vacation"
        """)
    
    # Main content area
    st.title("🤖 Gemini AI Assistant")
    st.markdown("Ask me anything! I can help with calculations, weather, and general questions.")
    
    # Initialize models
    if 'agent' not in st.session_state or 'generic_llm' not in st.session_state:
        with st.spinner("Initializing AI models..."):
            agent, generic_llm = initialize_models()
            st.session_state.agent = agent
            st.session_state.generic_llm = generic_llm
        st.success("✅ AI Assistant ready!")
    
    # Chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "mode_used" in message:
                st.caption(f"Mode: {message['mode_used']}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Determine which model to use
                    if mode == "🤖 Auto Mode (Recommended)":
                        use_tools = is_tool_query(prompt)
                        mode_used = "Tool Mode" if use_tools else "Chat Mode"
                    elif mode == "🛠️ Tool Mode":
                        use_tools = True
                        mode_used = "Tool Mode"
                    else:  # Chat Mode
                        use_tools = False
                        mode_used = "Chat Mode"
                    
                    # Get response
                    if use_tools:
                        response = st.session_state.agent.invoke({"input": prompt})
                        
                        # Extract the actual response text
                        if isinstance(response, dict):
                            response_text = response.get("output", str(response))
                        else:
                            response_text = str(response)
                    else:
                        response = st.session_state.generic_llm.invoke(prompt)
                        response_text = response.content
                    
                    # Display response
                    st.markdown(response_text)
                    st.caption(f"Mode: {mode_used}")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text,
                        "mode_used": mode_used
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with ❤️ using Streamlit and Gemini")

if __name__ == "__main__":
    main()
