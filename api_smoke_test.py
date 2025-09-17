#!/usr/bin/env python3
"""
Minimal smoke test for API startup without triggering background tasks.
Checks root and health endpoints using FastAPI TestClient.
"""
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.api_config.main import app

def run_smoke():
    client = TestClient(app)

    # Root endpoint
    r = client.get("/")
    assert r.status_code == 200, f"Root endpoint failed: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("status") == "healthy", f"Unexpected root status: {data}"
    print("✅ Root endpoint OK")

    # Health endpoint
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"Health endpoint failed: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("status") == "healthy", f"Unexpected health status: {data}"
    print("✅ Health endpoint OK")

    print("🎉 API smoke test passed")

if __name__ == "__main__":
    run_smoke()
