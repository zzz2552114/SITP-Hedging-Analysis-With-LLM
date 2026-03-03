import os
import sys
import asyncio
from datetime import date

# 插入模块搜索路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

async def go():
    from httpx import AsyncClient, ASGITransport
    from main import app
    from tortoise import Tortoise
    from app.models import ListedCompanyBase, AnnouncementMeta

    await Tortoise.init(modules={"models": ["app.models"]}, db_url="sqlite://:memory:")
    await Tortoise.generate_schemas()

    await ListedCompanyBase.create(
        stock_code="000001",
        company_name="平安",
        company_short_name="平安",
        market="SZSE"
    )
    
    await AnnouncementMeta.create(
        announcement_id="A-001",
        stock_code_id="000001",
        announcement_title="套期保值",
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
    print("STATUS", response.status_code)
    print("TEXT", response.text)

asyncio.run(go())
