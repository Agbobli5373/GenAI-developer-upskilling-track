#!/usr/bin/env python3
import os
import sys
from agent import create_agent
from dotenv import load_dotenv

load_dotenv()

def print_banner():
    """Print a welcome banner for the tool-using agent."""
    print("\n" + "="*60)
    print("🤖 GEMINI TOOL-USING AGENT 🤖".center(60))
    print("="*60)
    print("Available tools: Calculator and Weather")
    print("Type 'exit' or 'quit' to end the session")
    print("="*60 + "\n")

def main():
    """Main CLI interface for the tool-using agent."""
    # Check for API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please create a .env file with your Google API key or set it in your environment.")
        return
    
    # Create the agent
    try:
        print("Initializing Gemini agent...")
        agent = create_agent()
        print("Agent ready!")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return
    
    # Print welcome banner
    print_banner()
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ")
            
            # Check for exit command
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using the Gemini Tool-Using Agent! Goodbye!")
                break
            
            # Process the query with the agent
            response = agent.invoke({"input": user_input})
            
            # Display the response
            print(f"\n🤖 Gemini Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\nSession terminated by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()