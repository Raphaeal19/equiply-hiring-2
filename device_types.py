import json
import sqlite3
from pathlib import Path
from urllib.parse import quote

import client

DB_PATH = Path("cache/device_types.db")


def connect(create=False) -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if create:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS device_types (
                type TEXT PRIMARY KEY, category TEXT, equipment_function TEXT,
                synonyms TEXT, standard_lifespan INTEGER, proactive_lifespan INTEGER,
                extended_lifespan INTEGER
            );
            """
        )
    return conn


def download_device_types(conn: sqlite3.Connection, names: list[str]) -> list[str]:
    missing = []
    for i in range(0, len(names), 200):
        found = batch_device_types(names[i : i + 200])
        for name, t in found.items():
            if t is None:
                missing.append(name)
                continue
            conn.execute(
                "INSERT OR REPLACE INTO device_types VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    t["type"], t["category"], t["equipmentFunction"],
                    json.dumps(t["synonyms"]), t["standardLifespan"],
                    t["proactiveLifespan"], t["extendedLifespan"],
                ),
            )
    conn.commit()
    return missing


def get_device_type(name: str) -> dict:
    return client.get(f"device-types/{quote(name)}")["data"]


def batch_device_types(names: list[str]) -> dict[str, dict | None]:
    return client.post("device-types/batch", {"device_types": names})["data"]


def search_device_types(query: str, limit: int = 15) -> list[dict]:
    return client.post("device-types/search", {"query": query, "limit": limit})["data"]


def hybrid_search_device_types(query: str, limit: int = 15) -> list[dict]:
    return client.post("device-types/hybrid-search", {"query": query, "limit": limit})["data"]


def get_device_types(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM device_types").fetchall()


if __name__ == "__main__":
    pass
    # conn = connect(create=True)
    # download_device_types(conn=conn, )
    # print(search_device_types("iv pump"))
    # # print(download_device_types(conn, ["Infusion Pump", "Defibrillator"]))