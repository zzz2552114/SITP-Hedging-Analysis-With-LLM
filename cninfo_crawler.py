import requests
import json
import os
import time
import re
import pandas as pd
from datetime import datetime
import configparser
from urllib.parse import urljoin
import logging
import sys

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CnInfoCrawler:
    def __init__(self, config_file='config.ini'):
        """初始化爬虫，读取配置文件"""
        # 获取配置文件路径（兼容开发和打包环境）
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            base_path = os.path.dirname(sys.executable)
            config_path = os.path.join(base_path, config_file)
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_path, config_file)
            
        # 如果配置文件不存在，尝试在当前目录查找
        if not os.path.exists(config_path):
            config_path = config_file
            
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        
        # API基础URL
        self.base_url = "https://www.cninfo.com.cn/new/fulltextSearch/full"
        
        # 读取配置
        self.search_key = self.config.get('settings', 'search_key')
        self.start_date = self.config.get('settings', 'start_date')
        self.end_date = self.config.get('settings', 'end_date')
        filter_keywords_str = self.config.get('settings', 'filter_keywords')
        self.filter_keywords = [kw.strip() for kw in filter_keywords_str.split(',') if kw.strip()]
        self.page_size = self.config.getint('settings', 'page_size')
        self.data_path = self.config.get('settings', 'data_path')
        self.pdf_path = self.config.get('settings', 'pdf_path')
        self.excel_file = self.config.get('settings', 'excel_file')
        
        # 创建目录
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.pdf_path, exist_ok=True)
        
        # Excel文件完整路径
        self.excel_path = os.path.join(self.data_path, self.excel_file)
        
        # 已爬取的公告ID集合
        self.crawled_ids = set()
        
        # 加载已爬取的数据
        self.load_crawled_data()
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.cninfo.com.cn/new/index',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        logger.info(f"初始化完成，搜索关键词: {self.search_key}, 时间范围: {self.start_date} 至 {self.end_date}")
        logger.info(f"过滤关键词: {self.filter_keywords}")

    def load_crawled_data(self):
        """加载已爬取的数据，避免重复爬取"""
        if os.path.exists(self.excel_path):
            try:
                df = pd.read_excel(self.excel_path)
                if '公告ID' in df.columns:
                    self.crawled_ids = set(df['公告ID'].astype(str).tolist())
                    logger.info(f"已加载 {len(self.crawled_ids)} 条历史数据")
            except Exception as e:
                logger.error(f"加载历史数据失败: {e}")

    def get_announcements(self, page_num=1):
        """获取指定页的公告数据"""
        params = {
            'searchkey': self.search_key,
            'sdate': self.start_date,
            'edate': self.end_date,
            'isfulltext': 'false',
            'sortName': 'pubdate',
            'sortType': 'desc',
            'pageNum': page_num,
            'pageSize': self.page_size,
            'type': ''
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('announcements'):
                return data['announcements'], data.get('totalRecordNum', 0)
            return [], 0
        except Exception as e:
            logger.error(f"获取第 {page_num} 页数据失败: {e}")
            return [], 0

    def clean_title(self, title):
        """清理标题，去除<em>标签"""
        if not title:
            return ""
        # 去除<em>和</em>标签
        clean_title = re.sub(r'<em>|</em>', '', title)
        return clean_title.strip()
    
    def clean_filename(self, filename):
        """清理文件名，去除非法字符"""
        if not filename:
            return ""
        # Windows文件名非法字符: \ / : * ? " < > |
        # 替换为下划线
        clean_name = re.sub(r'[\\/:*?"<>|]', '_', filename)
        # 去除多余的空格和点
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        # 限制文件名长度
        if len(clean_name) > 150:
            clean_name = clean_name[:150]
        return clean_name

    def should_filter(self, title):
        """判断是否应该过滤该公告"""
        if not title:
            return False
            
        title = self.clean_title(title)
        for keyword in self.filter_keywords:
            if keyword in title:
                logger.debug(f"过滤公告: {title} (包含关键词: {keyword})")
                return True
        return False

    def format_date(self, timestamp):
        """格式化时间戳为日期字符串"""
        if not timestamp:
            return ""
        try:
            # 时间戳是毫秒级的，需要转换为秒
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"日期格式化失败: {e}")
            return ""

    def build_announcement_url(self, org_id, announcement_id, announcement_time):
        """构建公告详情页URL"""
        if not all([org_id, announcement_id, announcement_time]):
            return ""
        date_str = self.format_date(announcement_time)
        return f"https://www.cninfo.com.cn/new/disclosure/detail?orgId={org_id}&announcementId={announcement_id}&announcementTime={date_str}"

    def build_pdf_url(self, adjunct_url):
        """构建PDF下载URL"""
        if not adjunct_url:
            return ""
        return f"https://static.cninfo.com.cn/{adjunct_url}"

    def download_pdf(self, pdf_url, announcement_id, announcement_time, sec_name="", title=""):
        """下载PDF文件"""
        if not pdf_url:
            return None
            
        try:
            # 检查文件是否已存在
            date_str = self.format_date(announcement_time)
            # 构建新文件名：股票+时间+标题
            clean_sec_name = self.clean_filename(sec_name)
            clean_title = self.clean_filename(title)
            
            # 确保文件名各部分都有内容
            stock_part = clean_sec_name if clean_sec_name else "未知股票"
            title_part = clean_title if clean_title else "未知标题"
            
            filename = f"{stock_part}_{date_str}_{title_part}.pdf"
            file_path = os.path.join(self.pdf_path, filename)
            
            if os.path.exists(file_path):
                logger.debug(f"PDF已存在: {filename}")
                return file_path
                
            response = requests.get(pdf_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"PDF下载成功: {filename}")
            return file_path
        except Exception as e:
            logger.error(f"PDF下载失败 {announcement_id}: {e}")
            return None

    def crawl(self):
        """执行爬取任务"""
        logger.info("开始爬取公告数据...")
        
        all_data = []
        page_num = 1
        total_count = 0
        
        # 先获取第一页，确定总页数
        announcements, total_record_num = self.get_announcements(page_num)
        if not announcements:
            logger.warning("未获取到任何数据")
            return
            
        total_pages = (total_record_num + self.page_size - 1) // self.page_size
        logger.info(f"共 {total_record_num} 条记录，{total_pages} 页")
        
        # 处理第一页
        new_data = self.process_page(announcements)
        all_data.extend(new_data)
        total_count += len(new_data)
        
        # 处理剩余页面
        for page_num in range(2, total_pages + 1):
            logger.info(f"正在处理第 {page_num}/{total_pages} 页...")
            announcements, _ = self.get_announcements(page_num)
            if announcements:
                new_data = self.process_page(announcements)
                all_data.extend(new_data)
                total_count += len(new_data)
            time.sleep(0.5)  # 避免请求过快
            
        logger.info(f"爬取完成，共获取 {total_count} 条新数据")
        
        # 保存数据到Excel
        if all_data:
            self.save_to_excel(all_data)
        else:
            logger.info("没有新数据需要保存")

    def process_page(self, announcements):
        """处理一页的公告数据"""
        page_data = []
        
        for item in announcements:
            announcement_id = item.get('announcementId', '')
            
            # 跳过已爬取的公告
            if announcement_id in self.crawled_ids:
                logger.debug(f"跳过已爬取公告: {announcement_id}")
                continue
                
            # 检查是否需要过滤
            if self.should_filter(item.get('announcementTitle', '')):
                continue
                
            # 提取数据
            sec_code = item.get('secCode', '')
            sec_name = item.get('secName', '')
            title = self.clean_title(item.get('announcementTitle', ''))
            announcement_time = self.format_date(item.get('announcementTime', ''))
            org_id = item.get('orgId', '')
            adjunct_url = item.get('adjunctUrl', '')
            
            # 构建URL
            announcement_url = self.build_announcement_url(
                org_id, announcement_id, item.get('announcementTime', '')
            )
            pdf_url = self.build_pdf_url(adjunct_url)
            
            # 下载PDF，传递股票名称和标题
            pdf_path = self.download_pdf(pdf_url, announcement_id, item.get('announcementTime', ''), sec_name, title)
            
            # 添加到数据集
            data_item = {
                '股票代码': sec_code,
                '股票名称': sec_name,
                '标题': title,
                '时间': announcement_time,
                '公告链接': announcement_url,
                '公告ID': announcement_id,
                'PDF路径': pdf_path if pdf_path else ""
            }
            
            page_data.append(data_item)
            self.crawled_ids.add(announcement_id)
            
        return page_data

    def save_to_excel(self, data):
        """保存数据到Excel文件"""
        try:
            # 如果文件已存在，读取旧数据并合并
            if os.path.exists(self.excel_path):
                old_df = pd.read_excel(self.excel_path)
                new_df = pd.DataFrame(data)
                # 合并数据，去除重复
                combined_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['公告ID'], keep='last')
            else:
                combined_df = pd.DataFrame(data)
                
            # 按时间降序排序
            combined_df = combined_df.sort_values(by='时间', ascending=False)
            
            # 保存到Excel
            combined_df.to_excel(self.excel_path, index=False)
            logger.info(f"数据已保存到: {self.excel_path}")
        except Exception as e:
            logger.error(f"保存Excel失败: {e}")

if __name__ == "__main__":
    crawler = CnInfoCrawler()
    crawler.crawl()