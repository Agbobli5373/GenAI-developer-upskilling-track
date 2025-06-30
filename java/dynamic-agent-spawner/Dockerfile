FROM ollama/ollama

# Start Ollama server in the background, pull models, and then stop the server
RUN nohup ollama serve > /dev/null 2>&1 & \
    sleep 5 && \
    ollama pull phi3 && \
    ollama pull gemma:2b && \
    pkill ollama
