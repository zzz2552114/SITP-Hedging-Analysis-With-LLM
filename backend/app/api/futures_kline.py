import re
from fastapi import APIRouter, HTTPException, Query
from app.models import FuturesContract, FuturesDailyKline
from tortoise.expressions import Q
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class ContractItem(BaseModel):
    ts_code: str
    symbol: str
    name: str
    exchange: str
    fut_code: str
    pinyin_initial: str
    list_date: Optional[str] = None
    delist_date: Optional[str] = None


class ProductItem(BaseModel):
    fut_code: str
    exchange: str
    product_name: str   # 品种中文名，去掉尾部数字
    pinyin_initial: str


class KlineBar(BaseModel):
    trade_date: str
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    vol: Optional[float]
    amount: Optional[float]
    oi: Optional[float]
    settle: Optional[float]
    change1: Optional[float]
    change2: Optional[float]


def _strip_contract_suffix(name: str) -> str:
    """从合约名称中提取品种名，去掉尾部的合约月份数字及'主力/连续'等后缀"""
    return re.sub(r'[\d\s]*(?:主力|连续)?$', '', name).strip() or name


@router.get("/futures/products/grouped", response_model=dict)
async def list_products_grouped(
    keyword: Optional[str] = Query(None, description="模糊搜索品种名或代码"),
    exchange: Optional[str] = Query(None),
):
    """
    按首字母分组返回品种列表（已去重，每个 fut_code+exchange 只出现一次）。
    结构：{ "B": [{"fut_code": "CU", "exchange": "SHFE", "product_name": "沪铜", ...}], ... }
    """
    q = Q()
    if exchange:
        q &= Q(exchange=exchange)
    if keyword:
        q &= Q(name__icontains=keyword) | Q(fut_code__icontains=keyword)

    rows = await FuturesContract.filter(q).order_by("pinyin_initial", "fut_code").values(
        "fut_code", "exchange", "pinyin_initial", "name"
    )

    # 按 (fut_code, exchange) 去重：优先取含"主力"的那条名称
    seen: dict[tuple, dict] = {}
    for r in rows:
        key = (r["fut_code"], r["exchange"])
        if key not in seen or "主力" in r["name"]:
            seen[key] = r

    grouped: dict = {}
    for r in seen.values():
        initial = (r.get("pinyin_initial") or "#").upper()
        product_name = _strip_contract_suffix(r["name"])
        item = ProductItem(
            fut_code=r["fut_code"],
            exchange=r["exchange"],
            product_name=product_name,
            pinyin_initial=initial,
        ).model_dump()
        grouped.setdefault(initial, [])
        grouped[initial].append(item)

    return dict(sorted(grouped.items()))


@router.get("/futures/products/{fut_code}/contracts", response_model=List[ContractItem])
async def list_product_contracts(
    fut_code: str,
    exchange: Optional[str] = Query(None),
):
    """返回指定品种下的所有合约，按上市日期倒序（最新在前）"""
    q = Q(fut_code=fut_code)
    if exchange:
        q &= Q(exchange=exchange)

    items = await FuturesContract.filter(q).order_by("-list_date", "ts_code").values(
        "ts_code", "symbol", "name", "exchange", "fut_code",
        "pinyin_initial", "list_date", "delist_date"
    )
    return [ContractItem(**item) for item in items]


@router.get("/futures/contracts", response_model=List[ContractItem])
async def list_contracts(
    keyword: Optional[str] = Query(None),
    exchange: Optional[str] = Query(None),
):
    q = Q()
    if exchange:
        q &= Q(exchange=exchange)
    if keyword:
        q &= Q(name__icontains=keyword) | Q(ts_code__icontains=keyword)

    items = await FuturesContract.filter(q).order_by("pinyin_initial", "fut_code", "ts_code").values(
        "ts_code", "symbol", "name", "exchange", "fut_code",
        "pinyin_initial", "list_date", "delist_date"
    )
    return [ContractItem(**item) for item in items]


@router.get("/futures/contracts/grouped", response_model=dict)
async def list_contracts_grouped(
    keyword: Optional[str] = Query(None),
    exchange: Optional[str] = Query(None),
):
    q = Q()
    if exchange:
        q &= Q(exchange=exchange)
    if keyword:
        q &= Q(name__icontains=keyword) | Q(ts_code__icontains=keyword)

    items = await FuturesContract.filter(q).order_by("pinyin_initial", "fut_code", "ts_code").values(
        "ts_code", "symbol", "name", "exchange", "fut_code",
        "pinyin_initial", "list_date", "delist_date"
    )

    grouped: dict = {}
    for item in items:
        initial = (item.get("pinyin_initial") or "#").upper()
        grouped.setdefault(initial, [])
        grouped[initial].append(ContractItem(**item).model_dump())

    return dict(sorted(grouped.items()))


@router.get("/futures/kline/{ts_code}", response_model=List[KlineBar])
async def get_kline(
    ts_code: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(2000, ge=1, le=10000),
):
    contract = await FuturesContract.get_or_none(ts_code=ts_code)
    if not contract:
        raise HTTPException(status_code=404, detail=f"合约 {ts_code} 不存在")

    query = FuturesDailyKline.filter(ts_code_id=ts_code)
    if start_date:
        query = query.filter(trade_date__gte=start_date)
    if end_date:
        query = query.filter(trade_date__lte=end_date)

    bars = await query.order_by("trade_date").limit(limit).values(
        "trade_date", "open", "high", "low", "close",
        "vol", "amount", "oi", "settle", "change1", "change2"
    )
    return [KlineBar(**b) for b in bars]
