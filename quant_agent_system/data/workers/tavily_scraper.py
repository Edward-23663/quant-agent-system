# data/workers/tavily_scraper.py
import os
import json
import logging
import requests
from core.redis_bus import RedisBus
from core.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - TAVILY_SCRAPER - %(message)s')

class TavilyScraperWorker:
    def __init__(self):
        self.redis_bus = RedisBus()
        self.news_queue = "news_fetch_queue"
        self.vector_store = VectorStore()
        
        self.api_key = os.getenv("TAVILY_API_KEY", "your_tavily_key_here")

    def run(self):
        logging.info("🕷️ Tavily Scraper Worker 启动，监听非结构化新闻采集指令...")
        while True:
            task = self.redis_bus.pop_from_queue(self.news_queue, timeout=0)
            if task:
                self._process_task(task)

    def _process_task(self, task: dict):
        task_id = task.get('task_id')
        ticker = task.get('ticker')
        company_name = task.get('company_name', ticker)
        query = task.get('query', f"{company_name} 最新重大新闻 财务状况 催化剂事件")
        
        self.redis_bus.publish_status(task_id, f"📰 收到新闻采集指令: 正在通过 Tavily 搜索 [{query}]...")
        
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": False,
                "include_raw_content": True,
                "max_results": 5
            }
            response = requests.post(url, json=payload).json()
            
            if 'results' not in response:
                raise ValueError(f"Tavily API 响应异常: {response}")

            texts = []
            metadatas = []
            
            for item in response['results']:
                content = item.get('raw_content') or item.get('content')
                if not content: continue
                
                chunks = [content[i:i+500] for i in range(0, len(content), 500)]
                
                for chunk in chunks:
                    texts.append(chunk)
                    metadatas.append({
                        "ticker": ticker,
                        "source": item.get('url'),
                        "title": item.get('title'),
                        "score": item.get('score')
                    })

            if texts:
                self.redis_bus.publish_status(task_id, f"🧠 抓取到 {len(texts)} 条文本切片，正在进行本地向量化存储...")
                self.vector_store.add_documents(texts, metadatas)
                self.redis_bus.publish_status(task_id, f"✅ 向量化完成，已存入 LanceDB。")
                
                self.redis_bus.publish_status(task_id, f"SYSTEM_SIGNAL:NEWS_READY:{ticker}")
            else:
                self.redis_bus.publish_status(task_id, f"⚠️ 未抓取到有效的新闻内容。")

        except Exception as e:
            logging.error(f"新闻抓取/向量化失败: {e}")
            self.redis_bus.publish_status(task_id, f"❌ 新闻抓取失败: {e}")

if __name__ == "__main__":
    TavilyScraperWorker().run()
