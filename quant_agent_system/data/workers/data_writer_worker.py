# data/workers/data_writer_worker.py
import os
import json
import time
import logging
import duckdb
import pandas as pd
from core.redis_bus import RedisBus

logging.basicConfig(level=logging.INFO, format='%(asctime)s - WRITER - %(message)s')

class DataWriterWorker:
    def __init__(self):
        self.redis_bus = RedisBus()
        self.stream_name = "db_write_stream"
        self.group_name = "writer_group"
        self.consumer_name = "worker-1"
        
        db_path = "data/db/quant_data.duckdb"
        self.db = duckdb.connect(db_path, read_only=False)
        
        try:
            self.redis_bus.client.xgroup_create(self.stream_name, self.group_name, id='0', mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e): 
                logging.error(f"创建消费组失败: {e}")

    def run(self):
        logging.info("🚀 Data Writer Worker 启动，已独占 DuckDB 写锁，监听数据流...")
        while True:
            try:
                messages = self.redis_bus.client.xreadgroup(
                    self.group_name, self.consumer_name, {self.stream_name: ">"}, count=1, block=5000
                )
                if not messages:
                    continue

                for stream, msg_list in messages:
                    for msg_id, payload in msg_list:
                        self._process_payload(msg_id, payload)
                        
            except Exception as e:
                logging.error(f"Writer 循环异常: {e}")
                time.sleep(2)

    def _process_payload(self, msg_id: str, payload: dict):
        task_id = payload.get("task_id", "UNKNOWN")
        table = payload.get("table")
        records_json = payload.get("data")
        
        try:
            df = pd.DataFrame(json.loads(records_json))
            if df.empty:
                self.redis_bus.client.xack(self.stream_name, self.group_name, msg_id)
                return

            self.db.register('temp_df', df)
            self.db.execute("BEGIN TRANSACTION")
            
            columns = self.db.execute(f"DESCRIBE {table}").df()['column_name'].tolist()
            df_cols = [c for c in columns if c in df.columns]
            cols_str = ", ".join(df_cols)
            
            query = f"""
                INSERT INTO {table} ({cols_str}) 
                SELECT {cols_str} FROM temp_df
                ON CONFLICT DO NOTHING
            """
            self.db.execute(query)
            self.db.execute("COMMIT")
            self.db.unregister('temp_df')
            
            self.redis_bus.client.xack(self.stream_name, self.group_name, msg_id)
            logging.info(f"✅ 成功写入 {len(df)} 条数据至 {table} (MsgID: {msg_id})")
            
            self.redis_bus.publish_status(task_id, f"SYSTEM_SIGNAL:DATA_READY:{table}")
            
        except Exception as e:
            self.db.execute("ROLLBACK")
            logging.error(f"❌ 写入失败 (MsgID: {msg_id}): {e}")
            self.redis_bus.client.xack(self.stream_name, self.group_name, msg_id)

if __name__ == "__main__":
    DataWriterWorker().run()
