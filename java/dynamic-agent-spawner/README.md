# Dynamic Agent Spawner

A sophisticated AI-powered task execution system built with Quarkus and LangChain4j that dynamically spawns specialized AI agents to decompose and execute complex tasks through a multi-agent workflow.

## 🚀 Overview

The Dynamic Agent Spawner creates a collaborative AI system where different specialized agents work together to accomplish user goals:

1. **Instruction Generator Agent** - Analyzes the user's goal and creates tailored instructions for downstream agents
2. **Planner Agent** - Creates structured outlines and plans based on the generated instructions  
3. **Writer Agent** - Produces the final polished content based on the planner's output

## 🏗️ Architecture

```
User Request → Instruction Generator → Planner Agent → Writer Agent → Final Output
                      ↓                    ↓              ↓
                  (Generates)         (Creates Plan)  (Writes Content)
                 Instructions         
```

### Key Components

- **AgentSpawner**: Main orchestrator that coordinates the multi-agent workflow
- **InstructionGeneratorAgent**: Generates specialized instructions for planner and writer agents
- **TaskExecutionAgent**: Generic interface used by both planner and writer agents
- **DecomposedInstructions**: Data structure containing instructions for each agent type
- **TaskResource**: REST API endpoints for task execution and health monitoring

## 🛠️ Technology Stack

- **Framework**: Quarkus 3.x
- **AI Integration**: LangChain4j
- **LLM Provider**: Groq API (with OpenAI-compatible endpoints)
- **Models**: 
  - Default: `llama-3.1-8b-instant` (for logical/planning tasks)
  - Creative: `gemma2-9b-it` (for content generation)
- **Frontend**: Vanilla HTML/CSS/JavaScript with modern responsive design
- **Build Tool**: Maven

## 📋 Prerequisites

- Java 17 or higher
- Maven 3.8+
- Groq API key (sign up at [console.groq.com](https://console.groq.com))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dynamic-agent-spawner
```

### 2. Configure API Key

Create environment variable for your Groq API key:

**Windows:**
```cmd
set OPENAI_API_KEY=your_groq_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your_groq_api_key_here
```

### 3. Run the Application

```bash
./mvnw quarkus:dev
```

The application will start on `http://localhost:8080`

### 4. Use the Web Interface

Open your browser and navigate to `http://localhost:8080` to access the interactive web interface.

## 🌐 Web Interface Features

The application includes a modern, responsive web interface with:

- **Interactive Task Input**: Clean textarea for entering your goals
- **Real-time Progress Tracking**: Visual step-by-step execution monitoring
- **Detailed Results Display**: Shows instructions, planning output, and final results
- **Error Handling**: User-friendly error messages with retry functionality
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices

### Example Usage

1. Enter a task like: *"Write a short, upbeat, and encouraging twitter post about learning LangChain4j"*
2. Click "Execute Task"
3. Watch the three-step process unfold:
   - **Step 1**: Instruction generation for both agents
   - **Step 2**: Planning phase execution
   - **Step 3**: Final content creation

## 🔌 API Endpoints

### Core Endpoints

- `POST /tasks` - Execute a task (returns plain text)
- `POST /tasks/detailed` - Execute a task (returns detailed JSON response)
- `GET /tasks/health` - Health check endpoint

### Example API Usage

**Simple Task Execution:**
```bash
curl -X POST -H "Content-Type: text/plain" \
  --data "Write a professional email about project updates" \
  http://localhost:8080/tasks
```

**Detailed Task Execution:**
```bash
curl -X POST -H "Content-Type: text/plain" \
  --data "Create a marketing strategy outline" \
  http://localhost:8080/tasks/detailed
```

**Health Check:**
```bash
curl http://localhost:8080/tasks/health
```

## ⚙️ Configuration

### Model Configuration

The application is configured to use Groq's API with two specialized models:

```properties
# Default model (for logical/planning tasks)
quarkus.langchain4j.openai.chat-model.model-name=llama-3.1-8b-instant

# Creative model (for content generation)
quarkus.langchain4j.openai.creative.chat-model.model-name=gemma2-9b-it
```

### Timeout Settings

```properties
# API timeouts
quarkus.langchain4j.openai.timeout=30s
quarkus.rest-client.connect-timeout=30000
quarkus.rest-client.read-timeout=30000
```

### CORS Configuration

```properties
# Enable CORS for web interface
quarkus.http.cors=true
quarkus.http.cors.origins=*
quarkus.http.cors.methods=GET,POST,PUT,DELETE,OPTIONS
```

## 🔧 Development

### Project Structure

```
src/
├── main/
│   ├── java/org/acme/
│   │   ├── AgentSpawner.java           # Main orchestrator
│   │   ├── InstructionGeneratorAgent.java  # Instruction generation
│   │   ├── TaskExecutionAgent.java     # Generic agent interface
│   │   ├── DecomposedInstructions.java # Data structure
│   │   └── TaskResource.java           # REST endpoints
│   └── resources/
│       ├── application.properties      # Configuration
│       └── META-INF/resources/         # Web interface
│           ├── index.html             # Main UI
│           ├── style.css              # Responsive styling
│           └── script.js              # Interactive functionality
```

### Running Tests

```bash
./mvnw test
```

### Development Mode

Quarkus dev mode provides hot reload for rapid development:

```bash
./mvnw quarkus:dev
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
./mvnw package
docker build -f src/main/docker/Dockerfile.jvm -t dynamic-agent-spawner .
```

### Run with Docker

```bash
docker run -p 8080:8080 -e OPENAI_API_KEY=your_api_key dynamic-agent-spawner
```

### Docker Compose

```yaml
version: '3.8'
services:
  dynamic-agent-spawner:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## 🔍 Monitoring and Logging

### Health Monitoring

The application provides a health endpoint that returns service status:

```json
{
  "status": "healthy",
  "service": "Dynamic Agent Spawner",
  "timestamp": 1751290136735
}
```

### Logging Configuration

Enable debug logging for detailed execution traces:

```properties
quarkus.log.category."org.acme".level=DEBUG
quarkus.http.access-log.enabled=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Quarkus](https://quarkus.io/) - Supersonic Subatomic Java Framework
- [LangChain4j](https://docs.langchain4j.dev/) - Java implementation of LangChain
- [Groq](https://groq.com/) - Fast inference for LLM applications
- [Font Awesome](https://fontawesome.com/) - Icons for the web interface

## 📞 Support

For questions and support:

- Open an issue on GitHub
- Check the [Quarkus documentation](https://quarkus.io/guides/)
- Review [LangChain4j documentation](https://docs.langchain4j.dev/)

---

**Built with ❤️ using Quarkus and LangChain4j**
