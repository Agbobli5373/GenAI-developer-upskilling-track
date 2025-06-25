# Tool Calling Project

This project demonstrates a basic framework for tool calling with Python agents.

## Project Structure

- `agent.py` - Contains the main agent logic for tool calling.
- `main.py` - Entry point to run the tool-calling agent.
- `tools.py` - Defines the tools that can be called by the agent.
- `requirements.txt` - Lists the Python dependencies for the project.
- `.env` - Environment variables for configuration (not included in version control).

## Setup Instructions

1. **Clone the repository** and navigate to the `tool-calling` directory.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update values as needed (if applicable).

## Usage

To run the main agent:

```bash
python main.py
```

## Adding New Tools

- Define new tool functions in `tools.py`.
- Register them with the agent in `agent.py`.

Once the agent is running, you can ask it questions like:

"What's 342 * 15?"
"Calculate the square root of 169"
"What's the weather like in Accra?"
"Is it raining in Kumasi right now?"
"How much is 15% of 80?"
