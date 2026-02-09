# Podd Health Assistant Backend

FastAPI backend for the Podd health assistant, powered by LangGraph and LocusGraph.

## Setup

```bash
cp .env.example .env
# Edit .env with your credentials

python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload
```

## API Docs

Once running, visit `http://localhost:8000/docs` for the interactive API documentation.
