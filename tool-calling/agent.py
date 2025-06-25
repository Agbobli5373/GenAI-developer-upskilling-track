from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import CalculatorTool, WeatherTool
import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

def create_agent():
    """Create and return a LangChain agent using Gemini with tools."""
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
    
    # Initialize tools
    tools = [
        CalculatorTool(description="Performs mathematical calculations"),
        WeatherTool(description="Provides weather information for a location"),
    ]
    # Initialize language model (Gemini)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=SecretStr(os.getenv("GOOGLE_API_KEY") or "")
    )
    
    # Initialize agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent