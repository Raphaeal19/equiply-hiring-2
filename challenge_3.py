import json
import data
import client

PROCESS = "phsyi"

mfr_map = {}
for canon, spellings in json.load(open("cache/final_alias_map.json"))["aliases"].items():
    for s in spellings:
        mfr_map[s] = canon

dev_map = {}
for bucket, spellings in json.load(open("cache/device-alias-map.json"))["aliases"].items():
    for s in spellings:
        dev_map[s] = bucket

conn = data.connect()
rows = conn.execute(
    "SELECT facility_id, manufacturer, model_name, COUNT(*) AS n "
    "FROM records GROUP BY facility_id, manufacturer, model_name"
).fetchall()
totals = dict(conn.execute("SELECT facility_id, COUNT(*) FROM records GROUP BY facility_id").fetchall())
conn.close()

dictionary = {}
for r in rows:
    device = f"{mfr_map[r['manufacturer']]}||{r['model_name']}"
    key = dev_map.get(device, device)
    dictionary.setdefault(key, []).append({
        "raw_manufacturer": r["manufacturer"],
        "raw_model": r["model_name"],
        "count": r["n"],
        "source": r["facility_id"],
    })

payload = {"dictionary": dictionary, "process": PROCESS}

entries = [e for v in dictionary.values() for e in v]
print("devices:", len(dictionary), "| entries:", len(entries), "| records:", sum(e["count"] for e in entries), "of", sum(totals.values()))
for source, total in sorted(totals.items()):
    got = sum(e["count"] for e in entries if e["source"] == source)
    print(source, got, total, "OK" if got == total else "MISMATCH")
seen = [(e["source"], e["raw_manufacturer"], e["raw_model"]) for e in entries]
print("each source + spelling listed once:", len(seen) == len(set(seen)))
print("devices with more than one spelling:", sum(1 for v in dictionary.values() if len(v) > 1))
print("process length:", len(PROCESS), "(limit 12000)")

# if not PROCESS.strip() or len(PROCESS) > 12000:
#     raise SystemExit("Fill in PROCESS (up to 12000 characters) first.")
# print(client.post("q3/solution", payload))