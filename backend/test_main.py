import os
import sys
from fastapi.testclient import TestClient

# 添加路径映射以便识别 dev 包
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_pdfs():
    response = client.get("/api/data/pdfs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_results():
    response = client.get("/api/data/results")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_analyze_without_api_key():
    response = client.post("/api/analyze", json={
        "api_key": "",
        "model_settings": {}
    })
    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]
