import json
import os

# noinspection PyPackageRequirements
import pymysql

import settings
from common.app_logger import AppLogger


def _get_current_schema_version(cursor) -> float:
    cursor.execute("SHOW TABLES LIKE 'custom_data';")
    if cursor.fetchone():
        cursor.execute("SELECT data FROM custom_data WHERE code = 'db_schema_metadata';")
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            return data.get('version', 0)
    return 0


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
    current_schema_version = _get_current_schema_version(cursor)

    for file in sql_files:
        version_str = file.rstrip(".sql")
        try:
            version = float(version_str)
        except ValueError:
            logger.warning(f"Skipping invalid migration file name: {file}")
            continue
        if version <= current_schema_version:
            logger.info(f"Skipping already applied migration: {file}")
            continue
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
