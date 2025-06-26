# Tool Calling Project

This project demonstrates a framework for tool calling with Python agents, now featuring both a command-line interface and a modern Streamlit web UI.

## Project Structure

- `agent.py` - Contains the main agent logic for tool calling.
- `main.py` - Entry point to run the CLI tool-calling agent.
- `streamlit_app.py` - **NEW!** Streamlit web interface with enhanced features.
- `tools.py` - Defines the tools that can be called by the agent.
- `requirements.txt` - Lists the Python dependencies for the project.
- `run_streamlit.sh` / `run_streamlit.bat` - Scripts to easily launch the Streamlit app.
- `.env` - Environment variables for configuration (not included in version control).

## Features

### 🤖 Auto Mode (Recommended)

- Automatically detects whether your question needs tools or general chat
- Seamlessly switches between tool-enabled responses and general conversation

### 🛠️ Tool Mode

- Forces the use of available tools (Calculator and Weather)
- Best for mathematical calculations and weather queries

### 💭 Chat Mode

- Pure conversational AI for general questions
- Perfect for explanations, creative writing, planning, etc.

### Available Tools

- **Calculator**: Mathematical operations, trigonometry, logarithms
- **Weather**: Current weather information for any location worldwide

## Setup Instructions

1. **Clone the repository** and navigate to the `tool-calling` directory.

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file with the following variables:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

## Usage

### Option 1: Streamlit Web Interface (Recommended)

**Windows:**

```bash
run_streamlit.bat
```

**Linux/Mac:**

```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

**Manual launch:**

```bash
streamlit run streamlit_app.py
```

### Option 2: Command Line Interface

```bash
python main.py
```

## Example Queries

### Tool-Based Queries (Math & Weather)

- "What's 342 \* 15?"
- "Calculate the square root of 169"
- "Solve sin(30) + cos(60)"
- "What's the weather like in Accra?"
- "Is it raining in Kumasi right now?"
- "Temperature in Tokyo today"

### General Conversation

- "Explain quantum computing in simple terms"
- "Write a poem about artificial intelligence"
- "Help me plan a vacation to Europe"
- "What are the benefits of renewable energy?"
- "How does machine learning work?"

## Adding New Tools

- Define new tool functions in `tools.py`.
- Register them with the agent in `agent.py`.
- Update the keyword detection in `streamlit_app.py` if needed.

## Technical Details

- **LLM**: Google Gemini 2.5 Flash
- **Framework**: LangChain for tool orchestration
- **UI**: Streamlit for web interface
- **Tools**: Custom calculator and weather tools
