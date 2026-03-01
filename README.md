# Podd Health Assistant

locusgraph is context orchstration or prompt orchestration in a worlflow or automation

we are implicite memories of ai agents 

A comprehensive health assistant application with dual-database architecture (SQLite for authentication, LocusGraph SDK for health data storage).

## Project Structure

```
podd/
├── backend/
│   ├── src/              # Main application code
│   ├── tests/            # Test files
│   ├── docs/             # Documentation
│   ├── podd_env/         # Python virtual environment (dependencies installed here)
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment variables template
└── @bruno.podd/          # Bruno API collection
```

## Installation

### Prerequisites

- Python 3.12+
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd podd/backend
   ```

2. **Install dependencies** (dependencies are installed in `podd_env/`):
   ```bash
   # Install locusgraph SDK
   pip install git+https://github.com/locusgraph/bindings.git@v0.1.1#subdirectory=python

   # Install other dependencies from requirements.txt
   pip install -r requirements.txt
   ```

   Note: All dependencies are installed in `/backend/podd_env/`. Do not create a `.venv` folder.

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

## Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Authentication**: SQLite (Users, RefreshTokens)
- **Health Data Storage**: LocusGraph SDK (Event-based storage)
- **Documentation**: Bruno (API testing)
- **Workflows**: LangGraph

## Documentation

- [API Documentation](backend/docs/api_documentation.md)
- [Architecture](backend/docs/architecture.md)
- [Database Schema](backend/docs/database_schema.md)
- [Workflows](backend/docs/workflows.md)
- [Deployment](backend/docs/deployment.md)
- [Quick Reference](backend/docs/quick_reference.md)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black src/
isort src/
flake8 src/
```

### API Testing

Use Bruno collection in `@bruno.podd/` directory for API testing.

## License

[Add your license here]
