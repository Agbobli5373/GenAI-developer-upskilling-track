<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# RAG Monitoring and Evaluation Project Instructions

This is a comprehensive RAG (Retrieval-Augmented Generation) monitoring and evaluation system for Week 10 of the GenAI Developer Upskilling Track.

## Project Context

- **Focus**: Building production-ready monitoring and evaluation pipelines for RAG applications
- **Key Technologies**: LangSmith, LangChain, RAGAS, Streamlit, Prometheus
- **Evaluation Metrics**: Relevancy, faithfulness, hallucination detection, latency tracking
- **Architecture**: Modular design with separate evaluation, monitoring, dashboard, and reporting components

## Code Style and Standards

- Follow Python PEP 8 standards
- Use type hints for all function parameters and return values
- Implement comprehensive error handling and logging
- Use structured logging with appropriate log levels
- Include docstrings for all classes and functions
- Follow async/await patterns where applicable

## Key Components to Implement

1. **Evaluation Framework**: Custom evaluators using LangSmith and RAGAS
2. **Monitoring System**: Real-time performance tracking and logging
3. **Dashboard Interface**: Interactive Streamlit dashboard with visualizations
4. **Reporting Pipeline**: Automated report generation and export capabilities

## Specific Guidelines

- Integrate with LangSmith for automatic tracking of RAG runs
- Implement custom evaluation metrics for relevancy and hallucination detection
- Use structured logging with JSON format for better parsing
- Create modular, testable components with clear separation of concerns
- Implement proper configuration management using environment variables
- Use Pydantic models for data validation and serialization

## Testing Requirements

- Write unit tests for all evaluation metrics
- Include integration tests for the complete pipeline
- Mock external API calls in tests
- Test edge cases and error conditions

## Documentation Standards

- Include clear docstrings with parameter descriptions and return types
- Add inline comments for complex business logic
- Create example usage in docstrings
- Document configuration options and environment variables

## Performance Considerations

- Implement efficient batch processing for evaluations
- Use appropriate caching strategies for embeddings and retrievals
- Monitor memory usage for large document collections
- Implement proper async handling for I/O operations
