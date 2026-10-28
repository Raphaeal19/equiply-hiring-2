import data
import client

medc = ["A", "B", "C", "D"]


def build_payload():
  counts = {}
  for fac in medc:
    rows = conn.execute("SELECT manufacturer, model_name, COUNT(*) AS n FROM records WHERE facility_id = ? GROUP BY manufacturer, model_name", (fac,)).fetchall()
    counts[fac] = {(r["manufacturer"], r["model_name"]): r["n"] for r in rows}
  # print({fac: len(counts[fac]) for fac in medc})
  # print(counts)

  shared = set(counts["A"])
  for fac in ["B", "C", "D"]:
    shared = shared & set(counts[fac])
  # print(len(shared))

  models = []

  for manufacturer, model in shared:
    per_facility = {}
    for fac in medc:
      per_facility[fac] = counts[fac][(manufacturer, model)]
    models.append({
      "manufacturer": manufacturer,
      "model": model,
      "total": sum(per_facility.values()),
      "per_facility": per_facility
    })

  payload = {"models": models}
  return payload

  


conn = data.connect()
payload = build_payload()
# print(payload)
print(client.post("q2/solution", payload))