from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class ParsedHedgingItem(BaseModel):
    commodity: str
    hedging_limit: Optional[Decimal] = None
    hedging_direction: Optional[str] = None
    hedging_term: Optional[str] = None
    business_desc: Optional[str] = None
    
class AnnouncementParseResultRequest(BaseModel):
    items: List[ParsedHedgingItem]
    parse_status: int = 1  # 1: 成功, 2: 失败
    parse_error: Optional[str] = None
    llm_model: Optional[str] = None
    prompt_version: Optional[str] = None
