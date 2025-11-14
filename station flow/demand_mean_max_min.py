import pandas as pd

# 读取你的站点时段需求数据
df = pd.read_csv("station_record.csv")
### weekday=1时，说明是工作日###

# 确保 time_start 是整数小时
df["time_start"] = df["time_start"].astype(int)

# 核心聚合：按站点 station_id + 工作日 workday + 小时 time_start
agg = df.groupby(["station_id", "workday", "time_start"]).agg(
    borrow_mean=("borrow_demand", "mean"),
    borrow_max=("borrow_demand", "max"),
    borrow_min=("borrow_demand", "min"),
    return_mean=("return_demand", "mean"),
    return_max=("return_demand", "max"),
    return_min=("return_demand", "min"),
).reset_index()

# 保存总表
agg.to_csv("station_hourly_demand_prediction.csv", index=False)
print("已生成：station_hourly_demand_prediction.csv（包含所有站点）")
