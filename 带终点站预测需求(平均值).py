import pandas as pd
import numpy as np
from scipy.stats import poisson # 引入泊松分布（尽管 numpy 也有）

# 假设您的输入文件名为 "od.csv"
# 读取 OD 历史数据
df = pd.read_csv("od.csv")

# 确保必要字段类型正确
df['date'] = pd.to_datetime(df['date'])
df['start_station_id'] = df['start_station_id'].astype(str)
df['end_station_id'] = df['end_station_id'].astype(str)

# ---- 1. 统计历史总天数 & 预处理 ----
n_days = df['date'].nunique()
print("历史天数 =", n_days)

# 为计算零值做准备：将每日 trips 汇总 (确保同一天同一 OD-hour 只有一个记录)
daily_trips = df.groupby(['date', 'hour', 'start_station_id', 'end_station_id'])['trips'].sum().reset_index()

# 找出每天有 trips (>0) 发生的 OD-hour 组合
days_w_trips = daily_trips[daily_trips['trips'] > 0] 

# ---- 2. 对 (hour, start, end) 汇总所有天的统计量 ----

# 2.1 基础聚合 (总需求, 发生过 trips 的天数)
agg = daily_trips.groupby(['hour','start_station_id','end_station_id']).agg(
    total_trips=('trips', 'sum'),
    # 计算历史上发生过 trips (>0) 的天数
    days_with_trips=('trips', lambda x: (x > 0).sum())
).reset_index()

# 2.2 计算零膨胀率 (π) 和泊松率 (λ_c)
agg['days_with_zero_trips'] = n_days - agg['days_with_trips']
agg['zero_rate'] = agg['days_with_zero_trips'] / n_days # π
agg['overall_avg_trips'] = agg['total_trips'] / n_days # λ

# 计算非零计数过程的泊松率 (λ_c)： λ_c = λ / (1 - π)
#  必须处理零膨胀率为 1.0 的情况 (即从未发生过 trips 的 OD 对)，此时 λ_c 设为 0
agg['count_process_rate'] = np.where(
    agg['zero_rate'] < 1.0,
    agg['overall_avg_trips'] / (1 - agg['zero_rate']),
    0.0
)

# ---- 3. 零膨胀泊松预测函数 ----

def zip_predict(row):
    """双阶段 ZIP 随机抽样预测"""
    pi = row['zero_rate']         # 零膨胀率
    lambda_c = row['count_process_rate'] # 计数过程的泊松率

    # 1. 阶段一: 伯努利抽样 (决定是否为结构性零)
    # 如果随机数小于 π，则预测为 0 (结构性零)
    if np.random.rand() < pi:
        return 0

    # 2. 阶段二: 泊松抽样 (如果不是结构性零)
    # 确保 λ_c >= 0
    lam = max(lambda_c, 0)
    
    # 泊松分布随机抽样
    prediction = np.random.poisson(lam)
    
    return prediction

# ---- 4. 应用预测 ----

# 原始的平均需求（可保留作为基准）
agg['demand_avg'] = agg['overall_avg_trips']

# 零膨胀泊松预测
agg['demand_zip_poisson'] = agg.apply(zip_predict, axis=1)

# ---- 可选：取整（用于 ILP 模型） ----
agg['demand_up'] = agg['overall_avg_trips'].apply(lambda x: int(x) if x.is_integer() else int(x)+1)
agg['demand_0.5'] = agg['overall_avg_trips'].round().astype(int)

# ---- 导出结果 ----
agg.to_csv("od_hourly_zip_poisson.csv", index=False)

print("\n--- 零膨胀泊松预测完成 ---")
print("已输出到 od_hourly_zip_poisson.csv")
print("\n预测结果（前20行）：")
print(agg[['hour', 'start_station_id', 'end_station_id', 'demand_avg', 'zero_rate', 'demand_zip_poisson']].head(20))