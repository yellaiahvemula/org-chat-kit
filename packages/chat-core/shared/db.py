"""Database helpers."""

from __future__ import annotations

import psycopg2
from psycopg2.extras import RealDictCursor

from shared.config import ROOT_DIR, get_database_url


def get_connection():
    return psycopg2.connect(get_database_url())


def get_dict_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)


def init_database() -> None:
    sql = (ROOT_DIR / "scripts" / "init-db.sql").read_text()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()
