
import sqlite3
from typing import List
from dataclasses import dataclass

@dataclass
class AppConfig:
    key: str
    value: str
    category: str
    isEncrypted: bool
    description: str

class AppConfigProvider:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_all_configs(self) -> List[AppConfig]:
        configs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, description,category,isEncrypted FROM appconfig")
            rows = cursor.fetchall()
            for row in rows:
                configs.append(AppConfig(
                    key=row[0],
                    value=row[1],
                    description=row[2]
                ))
        return configs

    def get_config_by_key(self, key: str) -> AppConfig:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, description,category,isEncrypted FROM appconfig WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return AppConfig(
                    key=row[0],
                    value=row[1],
                    description=row[2],
                    category=row[3],
                    isEncrypted=row[4]
                )
        return None

    def update_config(self, config: AppConfig) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE appconfig SET value = ?, description = ? WHERE key = ?",
                (config.value, config.description, config.key)
            )
            return cursor.rowcount > 0
