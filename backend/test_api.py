import pytest
import os
import sys
from httpx import AsyncClient, ASGITransport
from datetime import date

# 插入模块搜索路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from main import app
from tortoise.contrib.test import tortoise_test_context
from app.models import ListedCompanyBase, AnnouncementMeta
import pytest_asyncio

@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_db():
    async with tortoise_test_context(["app.models"], db_url="sqlite://:memory:"):
        yield

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_get_companies_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/companies")
    assert response.status_code == 200
    assert response.json()["total"] == 0

@pytest.mark.asyncio
async def test_webhook_parse_result_error_not_found():
    # 试图解析一个不存在的公告id
    payload = {
        "items": [],
        "parse_status": 1,
        "llm_model": "test-model"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/announcements/not-exist-id/parsed", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "公告不存在"

@pytest.mark.asyncio
async def test_insert_company_and_webhook_success():
    # 先预置部分上下文数据
    await ListedCompanyBase.create(
        stock_code="000001",
        company_name="平安银行",
        company_short_name="平安",
        market="SZSE",
        establish_date=date(1987, 12, 22),
        list_date=date(1991, 4, 3)
    )
    
    await AnnouncementMeta.create(
        announcement_id="A-001",
        stock_code_id="000001",
        announcement_title="套期保值公告",
        publish_date=date(2024, 1, 1),
        biz_year=2024,
        storage_type="local",
        storage_key="test-123.pdf",
        parse_status=0
    )

    payload = {
        "items": [
            {
                "commodity": "铜",
                "hedging_limit": 50000.5,
                "hedging_direction": "买入套保",
                "hedging_term": "1年",
                "business_desc": "测试"
            }
        ],
        "parse_status": 1,
        "llm_model": "deepseek-test"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/announcements/A-001/parsed", json=payload)
        
    assert response.status_code == 200, f"Error: {response.text}"
    assert response.json()["status"] == "success"
    
    # 获取公告查看状态是否变更
    ann_meta = await AnnouncementMeta.get(announcement_id="A-001")
    assert ann_meta.parse_status == 1
