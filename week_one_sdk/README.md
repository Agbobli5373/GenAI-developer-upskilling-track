# Gemini AI Client - Production Ready

A production-ready Python client for Google's Gemini AI API with comprehensive error handling, logging, retry logic, and modular architecture.

## Features

- **🔄 Automatic Retry Logic**: Exponential backoff for handling server overload (503 errors)
- **🎯 Multiple Model Support**: Fallback between different Gemini models
- **📝 Comprehensive Logging**: Structured logging with file and console output
- **🛡️ Error Handling**: Custom exceptions and graceful error recovery
- **⚙️ Configurable**: Environment-based configuration with validation
- **🔧 Modular Design**: Separation of concerns with utils, config, and client classes
- **🏥 Health Checks**: Built-in API connectivity and status monitoring
- **📊 Streaming Support**: Real-time response streaming capabilities

## Project Structure

```
week_one_sdk/
├── main.py              # Main application entry point
├── gemini_client.py     # Core client class
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── exceptions.py       # Custom exception classes
├── requirements.txt    # Dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Installation

1. **Clone or navigate to the project directory**
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows Git Bash
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   LOG_LEVEL=INFO
   ```

## Usage

### Basic Usage

```python
from gemini_client import GeminiClient

# Initialize client
client = GeminiClient()

# Generate a response
response = client.generate_response("Who are you?")
print(response)
```

### Advanced Usage

```python
from gemini_client import GeminiClient

# Initialize with custom configuration
client = GeminiClient(
    models=["gemini-2.0-flash-exp", "gemini-1.5-flash"],
    max_retries=5,
    log_level="DEBUG",
    log_file="custom.log"
)

# Generate with custom parameters
response = client.generate_response(
    prompt="Explain quantum computing",
    temperature=0.7,
    max_tokens=500
)
```

### Streaming Response

```python
# Stream response in real-time
for chunk in client.generate_response_stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Health Check

```python
# Check API connectivity and status
health = client.health_check()
print(f"API Status: {'✅' if health['api_connectivity'] else '❌'}")
```

## Configuration

### Environment Variables

| Variable         | Description         | Default      |
| ---------------- | ------------------- | ------------ |
| `GEMINI_API_KEY` | Your Gemini API key | **Required** |
| `LOG_LEVEL`      | Logging level       | `INFO`       |

### Model Configuration

The client supports multiple Gemini models with automatic fallback:

- `gemini-2.0-flash-exp` (latest experimental)
- `gemini-1.5-flash` (fast and efficient)
- `gemini-1.5-pro` (high quality)

### Retry Configuration

- **Max Retries**: 3 attempts per model
- **Initial Delay**: 2 seconds
- **Backoff Multiplier**: 2.0 (exponential backoff)
- **Max Delay**: 60 seconds

## Error Handling

The client includes comprehensive error handling:

- **ConfigurationError**: Invalid configuration settings
- **AuthenticationError**: API key issues
- **ModelNotAvailableError**: No models available
- **ResponseError**: Response generation failures
- **RetryExhaustedError**: All retry attempts failed

## Logging

Structured logging is provided with:

- **Console Output**: Real-time status updates
- **File Logging**: Persistent log files (optional)
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **API Key Sanitization**: Secure logging of sensitive data

## Running the Application

```bash
# Basic demo
python main.py

# With virtual environment
source venv/Scripts/activate
python main.py
```

## Testing

```python
# Test API connectivity
python -c "from gemini_client import GeminiClient; print(GeminiClient().health_check())"
```

## Production Deployment

### Docker Support (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Environment Setup

1. **Set environment variables** in your deployment platform
2. **Configure logging** for your infrastructure
3. **Set up monitoring** for health checks
4. **Implement rate limiting** if needed

## Best Practices

1. **Always use environment variables** for API keys
2. **Monitor logs** for error patterns
3. **Implement health checks** in production
4. **Use appropriate retry limits** to avoid API quotas
5. **Handle exceptions gracefully** in your application

## API Reference

### GeminiClient Class

#### Constructor

```python
GeminiClient(
    api_key: Optional[str] = None,
    models: Optional[List[str]] = None,
    max_retries: Optional[int] = None,
    initial_retry_delay: Optional[float] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None
)
```

#### Methods

- `generate_response(prompt, **kwargs) -> str`
- `generate_response_stream(prompt, **kwargs) -> Generator[str, None, None]`
- `health_check() -> Dict[str, Any]`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install dependencies with `pip install -r requirements.txt`
2. **API Key Error**: Check your `.env` file and ensure `GEMINI_API_KEY` is set
3. **503 Server Error**: The client automatically retries with backoff
4. **No Response**: Check logs for detailed error information

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
client = GeminiClient(log_level="DEBUG")
```

## Contributing

1. Follow the existing code structure
2. Add type hints for all functions
3. Include comprehensive error handling
4. Update documentation for new features
5. Add logging for important operations

## License

This project is licensed under the MIT License.
