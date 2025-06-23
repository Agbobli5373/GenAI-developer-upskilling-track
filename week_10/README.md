# Week 10: RAG Monitoring and Evaluation System

A comprehensive monitoring and evaluation framework for Retrieval-Augmented Generation (RAG) applications with real-time metrics, performance tracking, and interactive dashboards.

## 🎯 Project Objectives

- **Evaluation**: Track relevancy, hallucinations, and answer quality using LangSmith and custom metrics
- **Logging**: Comprehensive logging of user queries, retrieved documents, and system latency
- **Reporting**: Interactive dashboards and automated reporting for RAG performance analysis
- **Monitoring**: Real-time performance monitoring with alerts and anomaly detection

## 🏗️ Architecture

```
week_10/
├── src/
│   ├── evaluation/          # Custom evaluation metrics and LangSmith integration
│   ├── monitoring/          # Logging, metrics collection, and performance tracking
│   ├── dashboard/           # Streamlit dashboard for visualization
│   ├── rag_system/          # Core RAG implementation for testing
│   └── utils/               # Shared utilities and configuration
├── data/
│   ├── datasets/            # Evaluation datasets
│   └── logs/                # Application logs
├── notebooks/               # Analysis and reporting notebooks
├── tests/                   # Unit and integration tests
└── configs/                 # Configuration files
```

## 🚀 Key Features

### 1. Evaluation Framework

- **LangSmith Integration**: Automatic tracking of RAG runs with detailed metrics
- **Custom Evaluators**: Relevancy, faithfulness, answer relevance, and context precision
- **RAGAS Integration**: Comprehensive RAG evaluation using proven metrics
- **Hallucination Detection**: Advanced techniques to identify and measure hallucinations

### 2. Monitoring System

- **Query Logging**: Structured logging of all user interactions
- **Performance Metrics**: Latency, throughput, and resource utilization tracking
- **Document Retrieval Analytics**: Analysis of retrieved document quality and relevance
- **Real-time Alerts**: Configurable alerts for performance degradation

### 3. Interactive Dashboard

- **Performance Overview**: Real-time metrics and KPI visualization
- **Query Analysis**: Deep dive into individual queries and responses
- **Trend Analysis**: Historical performance trends and patterns
- **Quality Metrics**: Relevancy scores, hallucination rates, and user satisfaction

### 4. Reporting Pipeline

- **Automated Reports**: Daily/weekly performance summaries
- **Quality Assessments**: Comprehensive evaluation reports
- **Comparative Analysis**: Performance comparison across different configurations
- **Export Capabilities**: PDF, CSV, and JSON export options

## 🛠️ Installation

1. **Create Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## 🔧 Configuration

Set up your environment variables in `.env`:

```bash
# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=rag-monitoring-week10

# Database Configuration
CHROMA_DB_PATH=./data/chroma_db

# Monitoring Configuration
LOG_LEVEL=INFO
METRICS_PORT=8000
```

## 🚀 Quick Start

1. **Initialize the System**:

   ```bash
   python src/setup_system.py
   ```

2. **Run Evaluation Pipeline**:

   ```bash
   python src/evaluation/run_evaluation.py
   ```

3. **Start Monitoring Dashboard**:

   ```bash
   streamlit run src/dashboard/app.py
   ```

4. **Generate Reports**:
   ```bash
   python src/reporting/generate_report.py
   ```

## 📊 Usage Examples

### Running Custom Evaluations

```python
from src.evaluation.custom_evaluators import RAGEvaluator

evaluator = RAGEvaluator()
results = evaluator.evaluate_batch(questions, contexts, answers)
```

### Monitoring RAG Performance

```python
from src.monitoring.performance_monitor import RAGMonitor

monitor = RAGMonitor()
with monitor.track_query("user_question"):
    response = rag_system.generate_answer(question)
```

### Dashboard Access

Navigate to `http://localhost:8501` after starting the Streamlit dashboard.

## 📈 Metrics Tracked

- **Relevancy Score**: How relevant retrieved documents are to the query
- **Faithfulness**: How faithful the answer is to the retrieved context
- **Answer Relevance**: How well the answer addresses the original question
- **Context Precision**: Precision of the retrieval system
- **Hallucination Rate**: Percentage of responses containing hallucinations
- **Latency Metrics**: Response time, retrieval time, generation time
- **User Satisfaction**: Implicit and explicit feedback scores

## 🔍 Advanced Features

- **A/B Testing Framework**: Compare different RAG configurations
- **Anomaly Detection**: Automatically detect performance issues
- **Custom Metric Development**: Framework for adding new evaluation metrics
- **Multi-language Support**: Evaluation across different languages
- **Integration APIs**: RESTful APIs for external monitoring tools

## 📝 Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Evaluators

1. Create new evaluator in `src/evaluation/custom_evaluators.py`
2. Register in `src/evaluation/registry.py`
3. Add tests in `tests/evaluation/`

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📚 Documentation

- [Evaluation Metrics Guide](docs/evaluation_metrics.md)
- [Dashboard User Guide](docs/dashboard_guide.md)
- [API Reference](docs/api_reference.md)
- [Configuration Options](docs/configuration.md)

## 🤝 Support

For questions and support, please refer to the course materials or create an issue in the repository.

---

**Week 10 Learning Outcomes**: By completing this project, you'll have hands-on experience with RAG monitoring, evaluation frameworks, and building production-ready monitoring systems for AI applications.
