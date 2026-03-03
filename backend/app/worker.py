import os
import sys
import logging
from datetime import datetime
from app.models import AnnouncementMeta, HedgingBusinessDetail, FuturesCommodityCatalog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEV_DIR = os.path.join(BASE_DIR, "dev")
sys.path.insert(0, DEV_DIR)

import sitp_recheck_2

logger = logging.getLogger(__name__)

async def process_unparsed_announcements(api_key: str, model_settings: dict = None):
    """
    定期拉取未解析公告（parse_status=0），读取存放在磁盘上的PDF，
    调用 LLM 解析，生成针对不同实体的 HedgingBusinessDetail 记录。
    支持幂等且失败后状态更新机制。
    """
    if not model_settings:
        model_settings = {
            'analysis': 'deepseek-v3.2',
            'processing': 'qwen-plus-2025-09-11',
            'recheck': 'qwen3-max',
            'translation': 'qwen-max'
        }

    # 读取最多10个未解析的公告（防止一次处理过多导致内存OOM或者API超时）
    unparsed_list = await AnnouncementMeta.filter(parse_status=0).limit(10)
    
    if not unparsed_list:
        logger.info("此时没有待解析的公告")
        return

    for ann in unparsed_list:
        logger.info(f"开始解析公告: {ann.announcement_title} ({ann.announcement_id})")
        # 如果是本地存储验证PDF是否存在
        file_path = os.path.join(BASE_DIR, "data", "pdfs", ann.storage_key) if ann.storage_type == "local" else ann.storage_key
        
        if not os.path.exists(file_path):
            ann.parse_status = 2 # 2=失败
            ann.parse_error = f"文件不存在: {file_path}"
            ann.parsed_at = datetime.now()
            await ann.save()
            continue
            
        try:
            # 这里的 sitp_recheck_2 假设它返回解析的结构化 json 数据
            # 现实中可能需要将脚本稍作重构抛出解析结果（目前它可能只是把结果落盘txt/json）
            # 当前演示调用它进行解析：
            # TODO: 真正应用中需改造 sitp_recheck_2 使之可传入特定 PDF 路径，并返回 dictionary 类型的结果
            # parsed_data = sitp_recheck_2.parse_single_pdf(file_path, api_key, model_settings)
            
            """
            虚拟一个 parsed_data，按需求结构化返回的可能是以下列表：
            [
                {
                    "commodity": "铜",
                    "hedging_limit": 50000.0,
                    "hedging_direction": "卖出套保",
                    "hedging_term": "1年",
                    "business_desc": "规避价格波动风险"
                }
            ]
            """
            
            # 由于实际代码 `sitp_recheck_2.py` 目前仍以处理整个目录方式工作，这里作示例模拟占位
            parsed_data = [] # 此处应该替换为调用 LLM 获取的真实数据。

            # 落库解析数据，需保持幂等性
            for item in parsed_data:
                # 寻找或者创建 Catalog ID (也可以通过大语言模型直接输出 Catalog_ID)
                catalog, created = await FuturesCommodityCatalog.get_or_create(
                    commodity_full_name=item["commodity"],
                    defaults={
                        "catalog_level": 1,
                        "commodity_short_name": item["commodity"]
                    }
                )

                await HedgingBusinessDetail.update_or_create(
                    announcement_id_id=ann.announcement_id,
                    catalog_id_id=catalog.catalog_id,
                    biz_year=ann.biz_year,
                    hedging_direction=item.get("hedging_direction"),
                    defaults={
                        "stock_code_id": ann.stock_code_id,
                        "hedging_limit": item.get("hedging_limit"),
                        "hedging_term": item.get("hedging_term"),
                        "business_desc": item.get("business_desc"),
                    }
                )
            
            # 更新元信息为成功
            ann.parse_status = 1
            ann.parse_error = None
            
        except Exception as e:
            logger.error(f"解析公告失败: {e}")
            ann.parse_status = 2
            ann.parse_error = str(e)
            
        ann.parsed_at = datetime.now()
        await ann.save()
