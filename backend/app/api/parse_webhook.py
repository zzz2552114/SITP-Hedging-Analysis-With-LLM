from fastapi import APIRouter, HTTPException
from app.models import AnnouncementMeta, HedgingBusinessDetail, FuturesCommodityCatalog, AnnouncementParseResult
from app.schemas_parse import AnnouncementParseResultRequest
from datetime import datetime
import json

router = APIRouter()

@router.post("/announcements/{announcement_id}/parsed")
async def submit_parse_result(announcement_id: str, payload: AnnouncementParseResultRequest):
    """
    接收来自外部大模型生成的分析结果并保存入库
    这是替代轮询 Worker 的一种基于推送式的解决方案
    """
    ann_meta = await AnnouncementMeta.get_or_none(announcement_id=announcement_id)
    if not ann_meta:
        raise HTTPException(status_code=404, detail="公告不存在")
        
    try:
        # 1. 记录原生的解析 JSON payload 留作追溯
        await AnnouncementParseResult.create(
            announcement_id=announcement_id,
            llm_model=payload.llm_model,
            prompt_version=payload.prompt_version,
            parsed_json=payload.model_dump(mode="json")
        )
        
        # 2. 如果解析成功，入库结构化的套保明细
        if payload.parse_status == 1 and payload.items:
            for item in payload.items:
                # 寻找或创建 Catalog
                catalog, _ = await FuturesCommodityCatalog.get_or_create(
                    commodity_full_name=item.commodity,
                    defaults={
                        "catalog_level": 1,
                        "commodity_short_name": item.commodity[:50]
                    }
                )
                
                # 幂等写入套保业务明细
                await HedgingBusinessDetail.update_or_create(
                    announcement_id=announcement_id,
                    catalog_id=catalog.catalog_id,
                    biz_year=ann_meta.biz_year,
                    hedging_direction=item.hedging_direction,
                    defaults={
                        "stock_code_id": ann_meta.stock_code_id,
                        "hedging_limit": item.hedging_limit,
                        "hedging_term": item.hedging_term,
                        "business_desc": item.business_desc,
                    }
                )
        
        # 3. 更新公告状态元数据
        ann_meta.parse_status = payload.parse_status
        ann_meta.parse_error = payload.parse_error
        ann_meta.parsed_at = datetime.now()
        await ann_meta.save()
        
        return {"status": "success", "message": "解析结果已成功入库"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
