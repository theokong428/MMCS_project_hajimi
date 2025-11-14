import pandas as pd
import json

#generalise format
pois_df = pd.read_csv("data_propress/raw_data/edinburgh_pois.csv")

pois_df.columns = pois_df.columns.str.strip()

pois_df.rename(columns={
    "lat": "latitude",
    "lon": "longitude",
    "latitude": "latitude",
    "longitude": "longitude"
}, inplace=True)

# label source
pois_df["source"] = "poi"

#generalise format
with open("data_propress/raw_data/bus_routes.dat", "r", encoding="utf-8") as f:
    data = json.load(f)

bus_rows = []
for service in data["services"]:
    service_name = service["name"]
    for route in service.get("routes", []):
        destination = route["destination"]
        for p in route.get("points", []):
            lat = p.get("latitude")
            lon = p.get("longitude")
            if lat is None or lon is None:
                continue
            bus_rows.append({
                "name": f"Bus {service_name} stop {p.get('stop_id')}" if p.get("stop_id") else f"Bus {service_name} stop (unknown)",
                "latitude": float(lat),
                "longitude": float(lon),
                "category": "bus_stop",
                "source": "bus"
            })

bus_df = pd.DataFrame(bus_rows)

#combine
combined = pd.concat([
    pois_df[['name','latitude','longitude','category','source']],
    bus_df[['name','latitude','longitude','category','source']]
], axis=0, ignore_index=True)

#reduction
before = len(combined)
combined = combined.drop_duplicates(subset=["latitude","longitude"])
after = len(combined)
print(f"Total before：{before}, Total after：{after}, reduction：{before - after}")

combined.to_csv("edinburgh_combined.csv", index=False)
print("generate edinburgh_combined.csv")
