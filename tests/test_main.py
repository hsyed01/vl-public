import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi import status
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

@pytest.mark.asyncio
async def test_get_will_listen_to_success():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
    response = await client.get(
      "/will-listen-to",
      params={
        "feed": "https://feeds.megaphone.fm/stuffyoushouldknow",
        "enclosure": "https://traffic.megaphone.fm/SN1234567890.mp3",
        "seconds": 600,
        "ua": "Test UA",
        "state": "CA",
        "genre": "Society",
        "content_duration": 1800
      }
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), float)


@pytest.mark.asyncio
async def test_get_missing_seconds():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
    response = await client.get("/will-listen-to", params={
      "feed": "https://feeds.megaphone.fm/stuffyoushouldknow",
      "enclosure": "https://feeds.megaphone.fm/episodes/stuffyoushouldknow/ep-1001.m4a"
    })
  assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_post_will_listen_to_success():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
    response = await client.post("/will-listen-to", json={
      "feed": "https://feeds.megaphone.fm/stuffyoushouldknow",
      "enclosure": "https://feeds.megaphone.fm/episodes/stuffyoushouldknow/ep-1001.m4a",
      "seconds": 600,
      "ua": "Spotify/8.9.0 iOS/15.3.1 iPhone13",
      "state": "Connecticut",
      "genre": "Society",
      "content_duration": 1800
    })
  assert response.status_code == status.HTTP_200_OK
  assert isinstance(response.json(), float)


@pytest.mark.asyncio
async def test_post_invalid_seconds():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
    payload = {
      "feed": "https://feeds.megaphone.fm/stuffyoushouldknow",
      "enclosure": "https://feeds.megaphone.fm/episodes/stuffyoushouldknow/ep-1001.m4a",
      "seconds": -10,
      "ua": "Test UA",
      "state": "NY",
      "genre": "Education",
      "content_duration": 1800
    }

    response = await client.post("/will-listen-to", json=payload)

    assert response.status_code == 400
    assert "seconds must be between 1 and 7200" in response.text

