#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
巨潮资讯网公告爬虫运行脚本
使用方法: python run_crawler.py
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from cninfo_crawler import CnInfoCrawler

def main():
    """主函数"""
    try:
        print("=" * 50)
        print("巨潮资讯网公告爬虫")
        print("=" * 50)
        
        # 创建爬虫实例
        crawler = CnInfoCrawler()
        
        # 执行爬取
        crawler.crawl()
        
        print("=" * 50)
        print("爬取任务完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()