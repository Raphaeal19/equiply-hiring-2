import sqlite3
from pathlib import Path

import client

DB_PATH = Path("cache/medical_institution.db")


def connect(create=False) -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if create:
      conn.executescript(
          """
          CREATE TABLE IF NOT EXISTS facilities (
              id TEXT PRIMARY KEY, name TEXT, record_count INTEGER
          );
          CREATE TABLE IF NOT EXISTS records (
              record_id TEXT PRIMARY KEY, facility_id TEXT, customer TEXT,
              department TEXT, billing_unit TEXT, ceid TEXT, serial_number TEXT,
              manufacturer TEXT, model_name TEXT, description_id TEXT,
              manufactured_date TEXT
          );
          """
    )
    return conn


def download_facilities(conn: sqlite3.Connection) -> None:
    for f in client.get("hospitals")["facilities"]:
        conn.execute(
            "INSERT OR REPLACE INTO facilities VALUES (?, ?, ?)",
            (f["id"], f["name"], f["record_count"]),
        )
    conn.commit()


def download_records(conn: sqlite3.Connection, facility_id: str) -> None:
    cursor = None
    while True:
        page = client.get(f"hospitals/{facility_id}/records", limit=500, cursor=cursor)
        conn.executemany(
            "INSERT OR REPLACE INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    r["record_id"], facility_id, r["Customer"],
                    r["Hospital Department"], r["Billing Business Unit"], r["CEID"],
                    r["Serial Number"], r["Manufacturer (MFG)"], r["Model Name"],
                    r["Description ID"], r["Manufactured Date"],
                )
                for r in page["records"]
            ],
        )
        conn.commit()
        cursor = page["next_cursor"]
        if cursor is None:
            break

def get_facilities(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM facilities").fetchall()


def get_records(conn: sqlite3.Connection, facility_id: str | None = None) -> list[sqlite3.Row]:
    if facility_id is None:
        return conn.execute("SELECT * FROM records").fetchall()
    return conn.execute("SELECT * FROM records WHERE facility_id = ?", (facility_id,)).fetchall()

if __name__ == "__main__":

  conn = connect(create=True)
  download_facilities(conn)
  for facility in get_facilities(conn):
      download_records(conn, facility["id"])
