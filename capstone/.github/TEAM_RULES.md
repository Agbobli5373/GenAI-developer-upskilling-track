# Team Development Rules

## Code Quality & Standards
- Follow PEP 8 for Python code and Google TypeScript style guide for frontend
- Write meaningful commit messages following the conventional commits format (feat:, fix:, docs:, etc.)
- Maintain test coverage above 80% for critical components
- Code reviews require at least one approval before merging
- Run linting and formatting before committing code

## Git Workflow
- `main` branch is protected and represents the production-ready state
- `develop` branch is the integration branch for features
- Create feature branches from `develop` named as `feature/[ticket-number]-short-description`
- Create fix branches as `fix/[ticket-number]-short-description`
- Rebase feature branches on `develop` before creating pull requests
- Use squash merging to keep history clean when merging to `develop`

## Documentation
- Document all public APIs using appropriate docstring formats
- Update README.md when adding new services or significant features
- Maintain up-to-date environment setup instructions
- Comment complex logic or algorithms
- Document LLM prompts and their purposes

## Testing
- Write tests for new features before or alongside implementation (TDD encouraged)
- Include both unit tests and integration tests
- Include performance tests for database and vector search operations
- Mock external APIs in tests to ensure stability

## CI/CD
- All PRs must pass CI checks before merging
- Failing tests block merges
- New deployments to staging require passing end-to-end tests
- Monitor staging for 24 hours after deployment before promoting to production

## Development Process
- Daily standup at 10:00 AM
- Demo sessions every two weeks at sprint end
- Ticket grooming sessions weekly
- Sprint planning bi-weekly
- Post retrospective notes in shared doc after each sprint

## LLM & AI Guidelines
- Log all significant LLM interactions for debugging and cost monitoring
- Review LLM outputs for accuracy before surfacing to users in critical features
- Implement LLM caching strategies for common queries
- Document prompt engineering decisions and version prompts
- Set up alerts for abnormal LLM usage patterns

## Security
- No secrets in code repositories (use environment variables)
- Regularly rotate API keys
- Implement proper input validation and output sanitization
- Follow OWASP security guidelines
- Conduct regular security reviews

## Performance
- Profile slow endpoints and queries regularly
- Optimize expensive database operations
- Implement appropriate indexing strategies
- Monitor and limit LLM token usage