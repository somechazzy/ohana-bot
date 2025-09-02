import os

# noinspection PyPackageRequirements
import pymysql

import settings
from common.app_logger import AppLogger


def apply_db_migrations():
    logger = AppLogger('db_migrations')
    sql_dir = os.path.join("scripts", "sql", "incremental_schema")
    sql_files = sorted(f for f in os.listdir(sql_dir) if f.endswith(".sql"))
    logger.info(f"Applying {len(sql_files)} database schema migrations(s)...")

    conn = pymysql.connect(
        host=settings.DB_CONFIG['host'],
        user=settings.DB_CONFIG['user'],
        password=settings.DB_CONFIG['password'],
        database=settings.DB_CONFIG['database'],
        port=settings.DB_CONFIG['port'],
        connect_timeout=5,
    )
    cursor = conn.cursor()

    for file in sql_files:
        with open(os.path.join(sql_dir, file), "r", encoding="utf-8") as f:
            sql_text = f.read()
        for statement in sql_text.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()

    cursor.close()
    conn.close()
    logger.info("Database schema migrations applied.")
