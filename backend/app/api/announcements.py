import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from app.models import AnnouncementMeta
from app.schemas import AnnouncementListResponse
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_STORAGE_DIR = os.path.join(BASE_DIR, "data", "pdfs")

router = APIRouter()

@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_announcements(
    stock_code: str = "",
    year: Optional[int] = None,
    parse_status: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100)
):
    query = AnnouncementMeta.all()
    
    if stock_code:
        query = query.filter(stock_code_id=stock_code)
    if year is not None:
        query = query.filter(biz_year=year)
    if parse_status is not None:
        query = query.filter(parse_status=parse_status)

    total = await query.count()
    items = await query.offset((page - 1) * size).limit(size).values(
        "announcement_id", "announcement_title", "publish_date", 
        "biz_year", "storage_type", "parse_status", "parsed_at", 
        "parse_error", "parse_version", stock_code_id="stock_code"
    )
    
    # 重命名关联外键字段以匹配 Schema
    for item in items:
        item["stock_code"] = item.pop("stock_code_id")
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }

@router.get("/announcements/{announcement_id}/pdf")
async def get_announcement_pdf(announcement_id: str):
    """从本地磁盘返回 PDF 文件（安全过滤处理）"""
    ann_meta = await AnnouncementMeta.get_or_none(announcement_id=announcement_id)
    if not ann_meta:
        raise HTTPException(status_code=404, detail="Announcement not found")
        
    if ann_meta.storage_type != "local":
        raise HTTPException(status_code=400, detail="PDF is not stored locally")
        
    file_path = os.path.join(PDF_STORAGE_DIR, ann_meta.storage_key)
    
    # 安全性检查: 避免目录穿透
    if not os.path.abspath(file_path).startswith(os.path.abspath(PDF_STORAGE_DIR)):
        raise HTTPException(status_code=403, detail="Invalid file path")
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
        
    # Return as file stream response for PDF
    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))
