import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_healthz():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/healthz")
        assert res.status_code == 200
        assert res.json()["ok"] is True


@pytest.mark.asyncio
async def test_inbound_and_list():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/inbound", content=b"hello")
        assert res.status_code == 200
        res = await ac.get("/api/requests")
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        first = data[0]
        assert first["method"] == "POST"
        rid = first["id"]
        res = await ac.get(f"/api/requests/{rid}")
        assert res.status_code == 200
        full = res.json()
        assert full["body_text"] == "hello"
        res = await ac.delete(f"/api/requests/{rid}")
        assert res.status_code == 200
