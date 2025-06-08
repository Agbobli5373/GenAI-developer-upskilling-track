# Gemini Contextual Memory Chatbot

A production-ready chatbot built with LangChain and Google Gemini that maintains contextual memory across conversations. This project demonstrates modern AI application development with proper modularization, testing, and configuration management.

## Features

- **Contextual Memory**: Maintains conversation history using LangChain's ConversationBufferMemory
- **Google Gemini Integration**: Powered by Google's latest Gemini AI model
- **Modern UI**: Clean Streamlit interface with real-time chat
- **Session Management**: Multiple conversation sessions with memory isolation
- **Production-Ready**: Proper error handling, logging, and environment configuration
- **Comprehensive Testing**: Unit tests with pytest for all core components
- **Modular Architecture**: Clean separation of concerns across modules

## Architecture

```
├── app.py                 # Main Streamlit application
├── llm_service.py         # Gemini LLM service and conversation chains
├── memory_manager.py      # Memory management and session handling
├── test_llm_service.py    # Unit tests for LLM service
├── test_memory_manager.py # Unit tests for memory manager
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
└── README.md             # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Google AI Studio API key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Agbobli5373/GenAI-developer-upskilling-track.git
cd week_three

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Google API key
GOOGLE_API_KEY=your_google_api_key_here
```

Get your Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 4. Running the Application

```bash
# Start the Streamlit app
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Usage

### Basic Chat
1. Open the application in your browser
2. Type messages in the chat input
3. The bot will respond using Gemini and remember the conversation

### Session Management
- **Clear Conversation**: Remove all messages from current session
- **New Session**: Start fresh with new session ID
- **View Memory**: Inspect the conversation memory buffer

### Memory Features
- Automatic conversation history tracking
- Configurable memory length (default: 10 exchanges)
- Memory trimming to prevent token limit issues
- Session isolation for multiple conversations

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI Studio API key | Required |
| `MODEL_NAME` | Gemini model to use | `gemini-1.5-flash` |
| `TEMPERATURE` | Response randomness (0-1) | `0.7` |
| `MAX_TOKEN_LIMIT` | Maximum tokens per request | `4000` |
| `MEMORY_KEY` | Key for storing chat history | `chat_history` |
| `MAX_MEMORY_LENGTH` | Max conversation exchanges to remember | `10` |
| `APP_TITLE` | Application title | `Gemini Contextual Memory Chatbot` |

### Model Configuration

The chatbot supports different Gemini models:
- `gemini-1.5-flash` (default): Best for text generation
- `gemini-pro-vision`: For multimodal inputs (future enhancement)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_memory_manager.py -v
pytest test_llm_service.py -v
```

### Test Categories

1.