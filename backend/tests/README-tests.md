Backend test instructions

1. Create a virtual environment and activate it.

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r backend/tests/requirements-dev.txt
```

2. Run tests from the repository root:

```bash
pytest -q
```

Notes:
- Tests avoid modifying project source files and use monkeypatching to stub DB calls.
