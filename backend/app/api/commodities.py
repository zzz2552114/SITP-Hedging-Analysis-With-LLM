from fastapi import APIRouter
from app.models import FuturesCommodityCatalog
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class CommodityItemResponse(BaseModel):
    catalog_id: int
    parent_catalog_id: Optional[int] = None
    catalog_level: int
    commodity_full_name: str
    commodity_short_name: str
    exchange: Optional[str] = None
    association_code: Optional[str] = None

@router.get("/commodities", response_model=List[CommodityItemResponse])
async def get_commodities(
    level: Optional[int] = None,
    parent_id: Optional[int] = None
):
    query = FuturesCommodityCatalog.all()
    
    if level is not None:
        query = query.filter(catalog_level=level)
        
    if parent_id is not None:
        query = query.filter(parent_catalog_id=parent_id)
        
    items = await query.order_by("catalog_id").values(
        "catalog_id", "parent_catalog_id", "catalog_level", 
        "commodity_full_name", "commodity_short_name", 
        "exchange", "association_code"
    )
    
    # 将字典转为响应模型格式
    return [CommodityItemResponse(**item) for item in items]
