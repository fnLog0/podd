# Podd Backend

Podd Health Assistant Backend — FastAPI service with auth, health tracking, medication, and more.

**Requirements:** Python 3.12 (3.13 may have compatibility issues with some dependencies.)

---

## Setup: `.venv` step by step

### 1. Go to the backend directory

```bash
cd backend
```

(Run from the project root, or use the full path to the backend folder.)

### 2. Create a virtual environment named `.venv`

```bash
python3 -m venv .venv
```

This creates a `.venv` folder in the backend directory.

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

When active, your prompt will usually show `(.venv)`.

### 4. Upgrade pip (recommended)

```bash
pip install --upgrade pip
```

### 5. Install dependencies

Use the project requirements (clean list; no frozen pins):

```bash
pip install -r requirements.txt
```

Or install in editable mode from `pyproject.toml`:

```bash
pip install -e .
```

**Note:** If you install a new library (e.g. `pip install some-package`), add it to `requirements.txt` (and to `pyproject.toml` if you use editable install) so others get the same dependencies.

### 6. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and set your API keys and secrets (e.g. `OPENAI_API_KEY`, `SARVAM_API_KEY`, `JWT_SECRET`).

### 7. Run the backend

From the **backend** directory (with `.venv` activated):

```bash
uvicorn src.main:app --reload
```

The API will be at **http://127.0.0.1:8000**. Docs: http://127.0.0.1:8000/docs.

### 8. Run tests (optional)

```bash
pytest
```

---

## Quick reference

| Task              | Command                          |
|-------------------|----------------------------------|
| Create `.venv`    | `python3 -m venv .venv`          |
| Activate          | `source .venv/bin/activate`      |
| Install deps      | `pip install -r requirements.txt`|
| Run server        | `uvicorn src.main:app --reload`  |
| Run tests         | `pytest`                         |

---

## Deactivating the virtual environment

When you're done working:

```bash
deactivate
```

Next time you work on the project, run `source .venv/bin/activate` again from the backend directory.
