from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import base64
from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
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
    headers_ordered: List[Tuple[str, str]]
    query: Dict[str, str]
    body_text: Optional[str] = None
    body_bytes_b64: Optional[str] = None
    body_length: int = 0
    raw_request_b64: Optional[str] = None


_requests: List[StoredRequest] = []
_next_id = 1


class WSManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self._clients.discard(ws)

    async def broadcast_json(self, data: dict):
        dead: List[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = WSManager()


@app.api_route("/inbound", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def inbound(request: Request):
    global _next_id
    body = await request.body()
    try:
        body_text = body.decode("utf-8") if body else None
    except UnicodeDecodeError:
        body_text = None
    # Capture ordered headers as seen by ASGI scope
    headers_scope = request.scope.get("headers", [])  # List[Tuple[bytes, bytes]]
    headers_ordered: List[Tuple[str, str]] = [
        (k.decode("latin-1"), v.decode("latin-1")) for (k, v) in headers_scope
    ]
    # Reconstruct a raw-like HTTP request stream (approximate; header casing may differ)
    http_version = request.scope.get("http_version", "1.1")
    target = request.url.path
    if request.url.query:
        target += f"?{request.url.query}"
    start_line = f"{request.method} {target} HTTP/{http_version}\r\n".encode("latin-1", "replace")
    header_lines = b"".join(
        (name.encode("latin-1", "replace") + b": " + value.encode("latin-1", "replace") + b"\r\n")
        for name, value in headers_ordered
    )
    raw_bytes = start_line + header_lines + b"\r\n" + (body or b"")
    item = StoredRequest(
        id=_next_id,
        method=request.method,
        path=request.url.path,
    ts=datetime.now(timezone.utc).timestamp(),
        ip=request.client.host if request.client else "",
        headers={k: v for k, v in request.headers.items()},
        headers_ordered=headers_ordered,
        query={k: v for k, v in request.query_params.items()},
        body_text=body_text,
        body_bytes_b64=(base64.b64encode(body).decode("ascii") if body and body_text is None else None),
        body_length=len(body) if body else 0,
        raw_request_b64=base64.b64encode(raw_bytes).decode("ascii"),
    )
    _requests.append(item)
    _next_id += 1
    # Broadcast summary to websocket listeners
    summary = RequestSummary(
        id=item.id,
        method=item.method,
        path=item.path,
        ts=item.ts,
        ip=item.ip,
        content_length=item.body_length,
    ).model_dump()
    await ws_manager.broadcast_json({"type": "new_request", "data": summary})
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

@app.get("/api/requests/{req_id}/raw")
async def get_request_raw(req_id: int):
    for r in _requests:
        if r.id == req_id:
            if not r.raw_request_b64:
                raise HTTPException(status_code=404, detail="No raw data available")
            raw = base64.b64decode(r.raw_request_b64)
            return Response(
                content=raw,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename= request-{r.id}.txt"
                },
            )
    raise HTTPException(status_code=404, detail="Request not found")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            # Keep the connection alive; ignore inbound messages
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)

# Optionally serve built frontend if present (Docker production)
_dist_dir = os.getenv("FRONTEND_DIST_DIR", "frontend-dist")
if os.path.isdir(_dist_dir):
    app.mount("/", StaticFiles(directory=_dist_dir, html=True), name="static")
