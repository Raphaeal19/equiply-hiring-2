import data
from collections import Counter
import client

def norm(value: str | None) -> str:
    return " ".join((value or "").lower().split())


def build_pairs(rows) -> list[dict]:
    counts = Counter()
    names = {}
    for r in rows:
        key = (norm(r["manufacturer"]), norm(r["model_name"]))
        counts[key] += 1
        names.setdefault(key, (r["manufacturer"] or "", r["model_name"] or ""))
    return [counts, names]


def build_payload(conn) -> dict:
    facilities = []
    for f in data.get_facilities(conn):
        counts, names = build_pairs(data.get_records(conn, f["id"]))
        pairs = [{"manufacturer": names[key][0], "model": names[key][1], "count": count} for key, count in counts.items()]

        facilities.append(
            {
                "facility": f["id"],
                "pairs": pairs,
                "most_common_model": max(pairs, key=lambda p: p["count"]),
            }
          )
    return {"facilities": facilities}




conn = data.connect()
payload = build_payload(conn)
print(client.post("q1/solution", payload))