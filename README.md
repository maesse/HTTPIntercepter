# HTTP Intercepter

A tiny debug HTTP interceptor: it exposes an `/inbound` endpoint that accepts any POST request, stores it in memory, and shows it in a minimalist Vue UI. Includes a FastAPI backend API for listing, viewing, and deleting captured requests.

[![CI](https://github.com/maesse/HTTPIntercepter/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/maesse/HTTPIntercepter/actions/workflows/ci.yml)

## Structure

- `backend/` — FastAPI app, pytest tests
- `frontend/` — Vue 3 (Vite) SPA
- `Dockerfile` — Multi-stage build to bundle both

## Backend (dev)

- Create a virtual env and install:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e backend[dev]
```

- Run the API locally:

```cmd
python -m uvicorn app.main:app --reload --port 8181 --app-dir backend
```

The frontend dev server (below) proxies `/api` and `/inbound` to 8181.

## Frontend (dev)

```cmd
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Docker

Build and run the combined image:

```cmd
docker build -t httpintercepter:local .
docker run --rm -p 8181:8181 httpintercepter:local
```

Open http://localhost:8181

## API

- `POST /inbound` — store inbound request; returns OK
- `GET /api/requests` — list summaries
- `GET /api/requests/{id}` — full record
- `DELETE /api/requests/{id}` — delete one
- `DELETE /api/requests` — delete all

Note: storage is in-memory and resets on restart.
