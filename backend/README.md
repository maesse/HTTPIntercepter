Backend quickstart

- Create venv and install deps:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

- Run dev server:

```cmd
python -m uvicorn app.main:app --reload --port 8181 --app-dir backend
```
