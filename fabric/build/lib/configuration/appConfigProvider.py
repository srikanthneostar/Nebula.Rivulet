import os
import sqlite3
from typing import List
from dataclasses import dataclass
import os
from configuration.NebulaCipher import decrypt

@dataclass
class AppConfig:
    key: str
    value: str
    description: str
    category: str
    isEncrypted: bool


class AppConfigProvider:
    def __init__(self):
        nebula_home = os.environ.get('NEBULA_HOME')
        if not nebula_home:
            raise EnvironmentError(
                "NEBULA_HOME environment variable is not defined")
        self.db_path = f"{nebula_home}/Nebula.Rivulet.db"
        self.create_db()
        self.SECRET_KEY = self.get_by_key_no_decrypt("SECRET_KEY").value
        self.SECRET_SALT = self.get_by_key_no_decrypt("SECRET_SALT").value

    def create_db(self):
        if not os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                               CREATE TABLE IF NOT EXISTS appconfig (
                                   key TEXT PRIMARY KEY,
                                   value TEXT,
                                   description TEXT,
                                   category TEXT,
                                   isEncrypted INTEGER
                               )
                           ''')
                conn.commit()

    def get_config(self, key: str) -> AppConfig:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appconfig WHERE key=?", (key,))
            row = cursor.fetchone()
            if row:
                return AppConfig(*row)
            else:
                raise ValueError(f"No configuration found for key: {key}")

    def get_config_by_category(self, category: str) -> List[AppConfig]:
        configs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT key, value, description,category,isEncrypted FROM appconfig where category=?", (category,))
            rows = cursor.fetchall()
            for row in rows:
                configs.append(AppConfig(
                    key=row[0],
                    value=row[1],
                    description=row[2],
                    category=row[3],
                    isEncrypted=row[4]
                ))
        return configs

    def add_config(self, config: AppConfig) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO appconfig (key, value, description, category, isEncrypted) VALUES (?, ?, ?, ?, ?)",
                (config.key, config.value, config.description,
                 config.category, config.isEncrypted)
            )
            return cursor.rowcount > 0

    def update_config(self, config: AppConfig) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE appconfig SET value = ?, description = ? WHERE key = ?",
                (config.value, config.description, config.key)
            )
            return cursor.rowcount > 0

    def get_by_key_no_decrypt(self, key) -> AppConfig:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT * FROM appconfig WHERE key=?", (key,)).fetchone()
            if result is None:
                raise ValueError(f"No configuration found for key: {key}")
            config = AppConfig(
                key=result[0],
                value=result[1],
                description=result[2],
                category=result[3],
                isEncrypted=bool(result[4]),
            )
            return config

    def decrypt_config(self, config: AppConfig):
        if config.isEncrypted:
            config.value = decrypt(config.value, secret_key=self.SECRET_KEY, salt=self.SECRET_SALT)
        return config