import sys
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List

# 把 dev 目录加入 sys.path 以便导入原有的爬虫和llm脚本
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_DIR = os.path.join(BASE_DIR, "dev")
sys.path.insert(0, DEV_DIR)

from cninfo_crawler import CnInfoCrawler
import sitp_recheck_2

app = FastAPI(title="SITP Hedging Analysis API", version="1.0.0")

# 配置 CORS 解决前后端同源问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 由于只是本地运行和展示demo，暂开放所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    search_key: str = "套期保值"
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    filter_keywords: str = ""
    page_size: int = 30

class AnalyzeRequest(BaseModel):
    api_key: str
    model_settings: Dict[str, str] = Field(default_factory=dict)
    # 期望结构: {'analysis': 'a', 'processing': 'b', 'recheck': 'c', 'translation': 'd'}

def run_crawler_sync(req: CrawlRequest):
    # 将模型实例转换为字典
    kwargs = req.model_dump()
    crawler = CnInfoCrawler(**kwargs)
    crawler.crawl()

def run_analyze_sync(req: AnalyzeRequest):
    # 提供模型代号到实际模型的映射
    model_map = {
        'a': 'deepseek-v3.2',
        'b': 'qwen-plus-2025-09-11',
        'c': 'qwen3-max',
        'd': 'qwen-max'
    }
    
    real_settings = {}
    for k, v in req.model_settings.items():
        # 如果用户传了字母 a, b，映射为真实模型，否则保留原始输入
        real_settings[k] = model_map.get(v, v)
        
    sitp_recheck_2.main(
        api_key=req.api_key,
        model_settings=real_settings
    )

@app.post("/api/crawl")
async def start_crawl(req: CrawlRequest):
    """触发爬虫任务"""
    try:
        # 使用 asyncio.to_thread 避免阻塞事件循环
        await asyncio.to_thread(run_crawler_sync, req)
        return {"status": "success", "message": "爬虫任务执行完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def start_analyze(req: AnalyzeRequest):
    """触发 LLM 分析任务"""
    # 基础安全性：检查 API Key 必须存在
    if not req.api_key or len(req.api_key) < 10:
        raise HTTPException(status_code=400, detail="无效或为空的 API Key")
        
    try:
        await asyncio.to_thread(run_analyze_sync, req)
        # API Key 绝对不会记录在任何落地日志中
        return {"status": "success", "message": "LLM 分析执行完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/pdfs", response_model=List[str])
def list_pdfs():
    """列出已下载的PDF文件"""
    pdf_dir = os.path.join(BASE_DIR, "data", "pdfs")
    if not os.path.exists(pdf_dir):
        return []
    # 仅允许返回 basename 数组，防止目录穿透攻击
    return [os.path.basename(f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

@app.get("/api/data/results", response_model=List[str])
def list_results():
    """列出 LLM 分析生成的TXT文件"""
    out_dir = os.path.join(BASE_DIR, "data", "out_txt")
    if not os.path.exists(out_dir):
        return []
    return [os.path.basename(f) for f in os.listdir(out_dir) if f.endswith('.txt')]

@app.get("/api/health")
def health_check():
    """系统健康检查"""
    return {"status": "ok"}
