# Gemini ChatCompletion Example

This project demonstrates how to interact with the Google Gemini LLM API using Python. It features secure API key management, logging, exception handling, and modular code.

## Features

- Loads Gemini API key from `.env` file
- Accepts user input and sends it to Gemini ChatCompletion endpoint
- Prints Gemini's response
- Logging and robust exception handling
- Modularized into `utils.py` and `main.py`

## Setup

1. **Clone the repository** and navigate to the project directory.
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
5. **Set up your API key:**
   - Copy your Gemini API key into the `.env` file:
     ```env
     GEMINI_API_KEY=your_actual_api_key_here
     ```

## Usage

Run the chat script:

```sh
python main.py
```

Type your message and press Enter. Gemini will respond!

## Files

- `main.py`: Entry point, handles user interaction and logging
- `utils.py`: API key loading, Gemini API call, error handling
- `.env`: Store your Gemini API key (never commit your real key)
- `requirements.txt`: Python dependencies

## References

- [How to use LLM APIs - Medium](https://medium.com/@lars.chr.wiik/how-to-use-llm-apis-openai-claude-google-50bc7ce2c8de)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs/get-started)

---

**Note:** This project is for educational purposes. Keep your API key secure and do not share it publicly.
