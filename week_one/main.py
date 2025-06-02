import logging
from gemini_pro import GeminiProClient
from gemini_flash import GeminiFlashClient

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )

def get_client(model_name):
    if model_name == "pro":
        return GeminiProClient()
    elif model_name == "flash":
        return GeminiFlashClient()
    else:
        raise ValueError("Unknown model")

def main():
    setup_logging()
    logger = logging.getLogger("main")
    print("Welcome to Gemini Chat! Type your message and press Enter (Ctrl+C to exit).\n")
    model_name = input("Choose model (pro/flash): ").strip().lower()
    try:
        client = get_client(model_name)
    except Exception as e:
        print(f"Error: {e}")
        return
    while True:
        try:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            logger.info(f"Sending prompt to Gemini {model_name}: {user_input}")
            response = client.generate_content(user_input)
            print(f"Gemini: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting Gemini Chat. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()