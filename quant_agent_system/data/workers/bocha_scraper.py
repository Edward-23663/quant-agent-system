# data/workers/bocha_scraper.py
import os
import json
import logging
import requests
from datetime import datetime
from core.redis_bus import RedisBus
from core.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - BOCHA_SCRAPER - %(message)s')

class BochaScraperWorker:
    def __init__(self):
        self.redis_bus = RedisBus()
        self.news_queue = "news_fetch_queue"
        self.vector_store = VectorStore()
        
        self.api_key = os.getenv("BOCHA_API_KEY", "")
        self.api_url = "https://api.bochaai.com/v1/web-search"

    def run(self):
        logging.info("🔍 Bocha Scraper Worker 启动，监听国内公告新闻采集指令...")
        while True:
            task = self.redis_bus.pop_from_queue(self.news_queue, timeout=0)
            if task:
                self._process_task(task)

    def _process_task(self, task: dict):
        task_id = task.get('task_id')
        ticker = task.get('ticker')
        company_name = task.get('company_name', ticker)
        query = task.get('query', f"{company_name} {ticker} 公告 财报")
        
        self.redis_bus.publish_status(task_id, f"📰 收到新闻采集指令: 正在通过 Bocha 搜索 [{query}]...")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'query': query,
                'sourceType': 'webSearch',
                'pageCount': 5
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise ValueError(f"Bocha API 响应异常: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if 'webPages' not in result or 'value' not in result.get('webPages', {}):
                raise ValueError(f"Bocha API 响应格式异常: {result}")
            
            texts = []
            metadatas = []
            
            for item in result['webPages']['value']:
                content = item.get('snippet') or item.get('summary', '')
                if not content:
                    continue
                
                chunks = [content[i:i+500] for i in range(0, len(content), 500)]
                
                for chunk in chunks:
                    texts.append(chunk)
                    crawled_date = item.get('dateLastCrawled')
                    if crawled_date:
                        news_date = crawled_date[:10]
                    else:
                        news_date = datetime.now().strftime("%Y-%m-%d")
                    metadatas.append({
                        "ticker": ticker,
                        "source": item.get('url'),
                        "title": item.get('name'),
                        "date": news_date
                    })

            if texts:
                self.redis_bus.publish_status(task_id, f"🧠 抓取到 {len(texts)} 条文本切片，正在进行本地向量化存储...")
                self.vector_store.add_documents(texts, metadatas)
                self.redis_bus.publish_status(task_id, f"✅ 向量化完成，已存入 LanceDB。")
                
                self.redis_bus.publish_status(task_id, f"SYSTEM_SIGNAL:NEWS_READY:{ticker}")
            else:
                self.redis_bus.publish_status(task_id, f"⚠️ 未抓取到有效的新闻内容。")

        except Exception as e:
            logging.error(f"Bocha 新闻抓取/向量化失败: {e}")
            self.redis_bus.publish_status(task_id, f"❌ Bocha 新闻抓取失败: {e}")

if __name__ == "__main__":
    BochaScraperWorker().run()
