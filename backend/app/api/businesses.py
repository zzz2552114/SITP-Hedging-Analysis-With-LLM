from fastapi import APIRouter, Query
from app.models import CompanyYearlyMainBusiness
from app.schemas import BusinessListResponse
from typing import Optional

router = APIRouter()

@router.get("/businesses", response_model=BusinessListResponse)
async def get_businesses(
    year: Optional[int] = None,
    industry_class: str = "",
    business_core: str = "",
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100)
):
    query = CompanyYearlyMainBusiness.all()
    
    if year is not None:
        query = query.filter(biz_year=year)
    if industry_class:
        query = query.filter(industry_class__icontains=industry_class)
    if business_core:
        query = query.filter(business_core__icontains=business_core)

    total = await query.count()
    items = await query.offset((page - 1) * size).limit(size)
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }
