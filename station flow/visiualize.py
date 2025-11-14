# pip install pandas matplotlib folium prophet

import pandas as pd
import matplotlib.pyplot as plt
import folium
from prophet import Prophet

# 1️⃣ 读取数据
df = pd.read_csv("station_record.csv")

# 转换时间格式（合并 date + time_start）
df["datetime"] = pd.to_datetime(df["date"]) + pd.to_timedelta(df["time_start"], unit="h")

# 计算总流量
df["total_demand"] = df["borrow_demand"] + df["return_demand"]

# ------------------------------------------------------------------
# 2️⃣ 时段流量柱状图（以小时平均）
hourly = df.groupby("time_start")[["borrow_demand", "return_demand", "total_demand"]].sum().reset_index()

plt.figure(figsize=(10, 5))
plt.bar(hourly["time_start"] - 0., hourly["borrow_demand"], width=0.3, label="Borrow")
plt.bar(hourly["time_start"], hourly["return_demand"], width=0.3, label="Return")
plt.xlabel("Hour of Day")
plt.ylabel("Demand")
plt.title("Hourly Bike Borrow/Return Demand")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("hourly_demand_bar.png", dpi=300)
plt.show()
print("✅ 时段柱状图已生成：hourly_demand_bar.png")

# ------------------------------------------------------------------
# 3️⃣ 地理分布可视化
geo = df.groupby(["station_id", "latitude", "longitude"])[["borrow_demand", "return_demand"]].sum().reset_index()
geo["total"] = geo["borrow_demand"] + geo["return_demand"]
geo["net"] = geo["return_demand"] - geo["borrow_demand"]

center = [geo["latitude"].mean(), geo["longitude"].mean()]
m = folium.Map(location=center, zoom_start=13, tiles="cartodb positron")

for _, row in geo.iterrows():
    color = "green" if row["net"] > 0 else "red"
    radius = max(3, min(row["total"] / 10, 20))  # 调整气泡大小
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=(f"Station {row['station_id']}<br>"
               f"Borrow: {row['borrow_demand']:.0f}<br>"
               f"Return: {row['return_demand']:.0f}<br>"
               f"Net: {row['net']:.0f}")
    ).add_to(m)

m.save("station_demand_map.html")
print("✅ 地理分布图已生成：station_demand_map.html（双击打开浏览器查看）")

# ------------------------------------------------------------------
# 4️⃣ 未来一个月流量预测（示例：全站总流量）
daily = df.groupby("date")[["borrow_demand", "return_demand", "total_demand"]].sum().reset_index()
daily["date"] = pd.to_datetime(daily["date"])

# 预测 borrow_demand
prophet_df = daily[["date", "total_demand"]].rename(columns={"date": "ds", "total_demand": "y"})
model = Prophet(weekly_seasonality=True, daily_seasonality=False)
model.fit(prophet_df)

future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 绘图
model.plot(forecast)
plt.title("Forecast of Total Bike Demand for Next 30 Days")
plt.tight_layout()
plt.savefig("future_demand_forecast.png", dpi=300)
plt.show()

print("✅ 未来30天流量预测图已生成：future_demand_forecast.png")