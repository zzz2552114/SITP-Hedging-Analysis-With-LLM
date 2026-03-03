from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Shared pagination response
class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list

# Companies APIs
class CompanyBase(BaseModel):
    stock_code: str
    company_name: str
    company_short_name: str
    market: str
    establish_date: Optional[date] = None
    list_date: Optional[date] = None

class CompanyListResponse(PaginatedResponse):
    items: List[CompanyBase]

# Businesses APIs
class BusinessBase(BaseModel):
    id: int
    stock_code: str
    biz_year: int
    main_business: str
    industry_class: str
    business_core: str

class BusinessListResponse(PaginatedResponse):
    items: List[BusinessBase]

# Commodities APIs
class CommodityBase(BaseModel):
    catalog_id: int
    parent_catalog_id: Optional[int] = None
    catalog_level: int
    commodity_full_name: str
    commodity_short_name: str
    exchange: Optional[str] = None
    association_code: Optional[str] = None

# Announcements APIs
class AnnouncementBase(BaseModel):
    announcement_id: str
    stock_code: str
    announcement_title: str
    publish_date: date
    biz_year: int
    storage_type: str
    parse_status: int
    parsed_at: Optional[datetime] = None
    parse_error: Optional[str] = None
    parse_version: Optional[str] = None

class AnnouncementListResponse(PaginatedResponse):
    items: List[AnnouncementBase]

# Hedging details APIs
class HedgingDetailBase(BaseModel):
    id: int
    announcement_id: str
    stock_code: str
    catalog_id: int
    biz_year: int
    hedging_limit: Optional[Decimal] = None
    hedging_direction: Optional[str] = None
    hedging_term: Optional[str] = None
    business_desc: Optional[str] = None

class HedgingListResponse(PaginatedResponse):
    items: List[HedgingDetailBase]

# Compare / Aggregate response
class HedgingCompanyCompareItem(BaseModel):
    stock_code: str
    company_name: str
    company_short_name: str
    has_hedging: bool
    year_hedging_limit: Decimal
    hedging_commodity_list: List[str]

class CompareHedgingResponse(BaseModel):
    biz_year: int
    business_core: str
    total_companies: int
    hedging_companies: int
    penetration_rate: float
    companies: List[HedgingCompanyCompareItem]
