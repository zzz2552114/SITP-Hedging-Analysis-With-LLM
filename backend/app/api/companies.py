from fastapi import APIRouter, Query
from app.models import ListedCompanyBase
from app.schemas import CompanyListResponse

router = APIRouter()

@router.get("/companies", response_model=CompanyListResponse)
async def get_companies(
    keyword: str = "",
    market: str = "",
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100)
):
    query = ListedCompanyBase.all()

    if keyword:
        # 支持公司名称或代码模糊搜索
        query = query.filter(company_name__icontains=keyword) | query.filter(stock_code__icontains=keyword)
    if market:
        query = query.filter(market=market)

    total = await query.count()
    items = await query.offset((page - 1) * size).limit(size)
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }
