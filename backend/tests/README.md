# Tests

Modular test layout by feature. Shared fixtures live in `conftest.py` at the repo root.

## Layout

```
tests/
├── conftest.py              # Shared fixtures (app, client, db, mock LocusGraph)
├── README.md                # This file
├── auth/                    # Auth API
│   └── test_auth.py         # Register, login, logout, refresh, me
├── health/                  # Health API
│   ├── test_food_log.py     # Food log CRUD
│   ├── test_vitals.py      # Vitals CRUD
│   └── test_insights_full.py  # Insights/recommendations check (script; run via `python -m tests.health.test_insights_full`)
├── medication/              # Medication API
│   ├── test_medication.py  # Medication CRUD
│   └── test_medication_schedule.py
├── profile/                 # Profile API
│   └── test_profile.py     # Profile GET/PUT/POST/DELETE
└── verification/            # Setup/verification scripts (not pytest)
    ├── test_imports.py     # Check route/schema imports
    ├── verify_imports.py   # Check import paths in route files
    ├── verify_phase2.py    # Phase 2 completion checks
    └── verify_backend_status.py  # Endpoint vs BACKEND_TODO status
```

## Run tests

From the **backend** directory (with `.venv` activated):

```bash
# All pytest tests
pytest

# By folder
pytest tests/auth/
pytest tests/health/
pytest tests/medication/
pytest tests/profile/

# By file
pytest tests/auth/test_auth.py
pytest tests/health/test_food_log.py -v

# With markers
pytest -m asyncio -v
```

## Verification scripts

These are standalone scripts (not pytest). Run from **backend**:

```bash
# Check all src imports load
python -m tests.verification.test_imports

# Check route import paths
python -m tests.verification.verify_imports

# Phase 2 health/insights checks
python -m tests.verification.verify_phase2

# Backend endpoint status vs BACKEND_TODO
python -m tests.verification.verify_backend_status
```

## Fixtures (conftest.py)

- **app** – FastAPI app
- **client** – `httpx.AsyncClient` with clean DB and mocked LocusGraph
- **clean_db** – Clears users and refresh tokens before/after each test
- **mock_locusgraph_service** – In-memory mock for LocusGraph
- **db_session** – Async DB session
- **test_user** – User `test@example.com` / `testpass123`
