from fastapi import APIRouter, Query, HTTPException
from app.models import HedgingBusinessDetail, ListedCompanyBase, CompanyYearlyMainBusiness
from app.schemas import HedgingListResponse, CompareHedgingResponse, HedgingCompanyCompareItem
from typing import Optional

router = APIRouter()

@router.get("/hedges", response_model=HedgingListResponse)
async def get_hedges(
    year: Optional[int] = None,
    catalog_id: Optional[int] = None,
    stock_code: str = "",
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100)
):
    query = HedgingBusinessDetail.all()
    
    if year is not None:
        query = query.filter(biz_year=year)
    if catalog_id is not None:
        query = query.filter(catalog_id_id=catalog_id)
    if stock_code:
        query = query.filter(stock_code_id=stock_code)

    total = await query.count()
    items = await query.offset((page - 1) * size).limit(size).values(
        "id", "biz_year", "hedging_limit", "hedging_direction", 
        "hedging_term", "business_desc",
        announcement_id_id="announcement_id",
        stock_code_id="stock_code",
        catalog_id_id="catalog_id"
    )
    
    for item in items:
        item["announcement_id"] = item.pop("announcement_id_id")
        item["stock_code"] = item.pop("stock_code_id")
        item["catalog_id"] = item.pop("catalog_id_id")
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }

@router.get("/compare/hedging_by_business", response_model=CompareHedgingResponse)
async def compare_hedging_by_business(
    year: int = Query(..., description="业务年份"),
    business_core: str = Query(..., description="过滤的公司核心主营行业")
):
    # 1. 查找此年份下符合该核心主营业务的所有公司
    companies_q = CompanyYearlyMainBusiness.filter(
        biz_year=year,
        business_core=business_core
    ).prefetch_related("stock_code")
    
    business_records = await companies_q
    
    if not business_records:
        return CompareHedgingResponse(
            biz_year=year, business_core=business_core,
            total_companies=0, hedging_companies=0,
            penetration_rate=0, companies=[]
        )

    # 提取符合条件的公司股票代码
    stock_codes = [b.stock_code.stock_code for b in business_records]
    
    # 2. 查询这些公司在同一年度的套保信息
    # 需联合 FuturesCommodityCatalog 取得商品名称
    hedging_records = await HedgingBusinessDetail.filter(
        biz_year=year,
        stock_code_id__in=stock_codes
    ).prefetch_related("catalog")
    
    # 3. 数据融合比对：统计公司并聚合额度假单
    hedging_map = {}
    for h in hedging_records:
        sc = h.stock_code_id
        if sc not in hedging_map:
            hedging_map[sc] = {"limit": 0, "commodities": set()}
            
        if h.hedging_limit:
            # 简化相加累和，实际可能需要换算由于是多条公告
            hedging_map[sc]["limit"] += float(h.hedging_limit)
        if h.catalog and h.catalog.commodity_full_name:
            hedging_map[sc]["commodities"].add(h.catalog.commodity_full_name)

    # 4. 生成返回结果
    result_companies = []
    hedging_count = 0
    
    for b in business_records:
        company_info = b.stock_code
        sc = company_info.stock_code
        has_hedging = sc in hedging_map
        
        limit = hedging_map[sc]["limit"] if has_hedging else 0.0
        cmdt_list = list(hedging_map[sc]["commodities"]) if has_hedging else []
        
        if has_hedging:
            hedging_count += 1
            
        result_companies.append(HedgingCompanyCompareItem(
            stock_code=sc,
            company_name=company_info.company_name,
            company_short_name=company_info.company_short_name,
            has_hedging=has_hedging,
            year_hedging_limit=limit,
            hedging_commodity_list=cmdt_list
        ))

    penetration_rate = hedging_count / len(result_companies) if result_companies else 0.0

    return CompareHedgingResponse(
        biz_year=year,
        business_core=business_core,
        total_companies=len(result_companies),
        hedging_companies=hedging_count,
        penetration_rate=penetration_rate,
        companies=result_companies
    )
