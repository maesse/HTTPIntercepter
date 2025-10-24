from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
import base64
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel

app = FastAPI(title="HTTP Intercepter Backend")


class RequestSummary(BaseModel):
    id: int
    method: str
    path: str
    ts: float
    ip: str
    content_length: int


class StoredRequest(BaseModel):
    id: int
    method: str
    path: str
    ts: float
    ip: str
    headers: Dict[str, str]
    query: Dict[str, str]
    body_text: Optional[str] = None
    body_bytes_b64: Optional[str] = None
    body_length: int = 0


_requests: List[StoredRequest] = []
_next_id = 1


@app.api_route("/inbound", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def inbound(request: Request):
    global _next_id
    body = await request.body()
    try:
        body_text = body.decode("utf-8") if body else None
    except UnicodeDecodeError:
        body_text = None
    item = StoredRequest(
        id=_next_id,
        method=request.method,
        path=request.url.path,
        ts=datetime.utcnow().timestamp(),
        ip=request.client.host if request.client else "",
        headers={k: v for k, v in request.headers.items()},
        query={k: v for k, v in request.query_params.items()},
        body_text=body_text,
        body_bytes_b64=(base64.b64encode(body).decode("ascii") if body and body_text is None else None),
        body_length=len(body) if body else 0,
    )
    _requests.append(item)
    _next_id += 1
    return Response(content="OK", media_type="text/plain")


@app.get("/api/requests", response_model=List[RequestSummary])
async def list_requests():
    return [
        RequestSummary(
            id=r.id,
            method=r.method,
            path=r.path,
            ts=r.ts,
            ip=r.ip,
            content_length=r.body_length,
        )
        for r in reversed(_requests)
    ]


@app.get("/api/requests/{req_id}", response_model=StoredRequest)
async def get_request(req_id: int):
    for r in _requests:
        if r.id == req_id:
            return r
    raise HTTPException(status_code=404, detail="Request not found")


@app.delete("/api/requests/{req_id}")
async def delete_request(req_id: int):
    global _requests
    before = len(_requests)
    _requests = [r for r in _requests if r.id != req_id]
    if len(_requests) == before:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"ok": True}


@app.delete("/api/requests")
async def delete_all_requests():
    _requests.clear()
    return {"ok": True}


@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/")
async def index():
    return {"name": "http-intercepter", "status": "running"}

# Optionally serve built frontend if present (Docker production)
_dist_dir = os.getenv("FRONTEND_DIST_DIR", "frontend-dist")
if os.path.isdir(_dist_dir):
    app.mount("/", StaticFiles(directory=_dist_dir, html=True), name="static")
