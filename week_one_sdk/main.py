"""
Main application entry point for the Gemini AI client.
"""
import logging
from typing import Optional

from gemini_client import GeminiClient
from exceptions import (
    ConfigurationError,
    AuthenticationError,
    ModelNotAvailableError,
    ResponseError
)


def main() -> None:
    """
    Main function to demonstrate the Gemini AI client.
    """
    try:
        # Initialize the client with production-ready configuration
        client = GeminiClient(
            log_level="INFO",
            log_file="gemini_client.log"
        )
        
        # Perform health check
        print("Performing health check...")
        health_status = client.health_check()
        
        if not health_status.get("api_connectivity", False):
            print("⚠️  API connectivity issues detected. Check logs for details.")
            return
        
        print("✅ Health check passed!")
        print(f"Available models: {', '.join(health_status['models'])}")
        
        # Generate response
        prompt = "Who are you? Please provide a brief introduction."
        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")
        
        try:
            response = client.generate_response(prompt)
            print(f"\n\n✅ Response completed successfully!")
            print(f"Response length: {len(response)} characters")
            
        except ModelNotAvailableError as e:
            print(f"❌ No models available: {e}")
        except ResponseError as e:
            print(f"❌ Response generation failed: {e}")
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set.")
        
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        print("Please check your API key.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Unexpected error in main function")


def demo_streaming() -> None:
    """
    Demonstrate streaming response functionality.
    """
    try:
        client = GeminiClient(log_level="INFO")
        
        prompt = "Tell me a short story about artificial intelligence."
        print(f"Streaming response for: {prompt}\n")
        
        full_response = ""
        for chunk in client.generate_response_stream(prompt):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print(f"\n\n✅ Streaming completed! Total length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Streaming demo failed: {e}")
        logging.exception("Error in streaming demo")


if __name__ == "__main__":
    print("🚀 Starting Gemini AI Client Demo")
    print("=" * 50)
    
    # Run main demo
    main()
    
    # Uncomment to run streaming demo
    # print("\n" + "=" * 50)
    # print("🔄 Streaming Demo")
    # print("=" * 50)
    # demo_streaming()