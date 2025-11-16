"""
最终版：用清洗好的 OD 平均需求运行多时段共享单车规划模型
依赖：pandas, numpy, pulp
"""

import pandas as pd
import numpy as np
import pulp
import math

# ================================
# 读取清洗后的 OD 数据
# ================================

#df = pd.read_csv("od_hourly_avg.csv")

#0膨胀poisson用下面这个
df = pd.read_csv("od_hourly_zip_poisson.csv")

# 确保 station 是字符串
df['start_station_id'] = df['start_station_id'].astype(str)
df['end_station_id']   = df['end_station_id'].astype(str)

# =================================
# 参数：成本（无需建站成本）
# =================================
r1 = 3     # 每辆车成本
r2 = 10    # 每个车位成本

# 选择需求字段： demand_up 或 demand_0.5
DEMAND_COL = "demand_zip_poisson"    # 或 "demand_up"

#DEMAND_COL = "demand_poisson"    

# ================================
# 整理 station index
# ================================
stations = sorted(pd.unique(pd.concat([df['start_station_id'], df['end_station_id']])))
N = len(stations)
station_to_idx = {z:i for i,z in enumerate(stations)}

df['i_idx'] = df['start_station_id'].map(station_to_idx)
df['j_idx'] = df['end_station_id'].map(station_to_idx)

# ================================
# 时段 = 自然小时（1..24）
# ================================
hours = sorted(df['hour'].unique())
K = max(hours)
print("使用自然小时 K =", K)

# ================================
# 构造 B[i,j,k]
# ================================
B = np.zeros((N, N, K+1), dtype=int)

for _, row in df.iterrows():
    i = row['i_idx']
    j = row['j_idx']
    k = int(row['hour'])
    demand = int(row[DEMAND_COL])
    if 1 <= k <= K:
        B[i,j,k] = demand

# ================================
# 构造旅行时间 t(i,j)
# 简化：1 小时内归还 → t = 1（或可设 >1）
# ================================
t = np.ones((N,N), dtype=int)

# ================================
# 计算 R[j,i,k] = B[j,i,k-t]
# ================================
R = np.zeros_like(B)

for i in range(N):
    for j in range(N):
        tij = t[i,j]
        for k in range(1, K+1):
            if k - tij > 0:
                R[i,j,k] = B[i,j,k-tij]

# ================================
# 构建 ILP 模型
# ================================
model = pulp.LpProblem("Bike_Planning", pulp.LpMinimize)

# x_i = initial bikes
# y_i = total parking capacity
xi = {i: pulp.LpVariable(f"x_{i}", lowBound=0, cat="Integer") for i in range(N)}
yi = {i: pulp.LpVariable(f"y_{i}", lowBound=0, cat="Integer") for i in range(N)}

# 初始最大停车位上界
MAX_PARK = 30    # 可改得更大

model += pulp.lpSum([r1 * xi[i] + r2 * yi[i] for i in range(N)])

# ================================
# 递推变量
# ================================
Vi = {}
Li = {}
A = {}
LA = {}

for i in range(N):
    for k in range(1, K+1):
        Vi[(i,k)] = pulp.LpVariable(f"V_{i}_{k}", lowBound=0, cat="Integer")
        Li[(i,k)] = pulp.LpVariable(f"L_{i}_{k}", lowBound=0, cat="Integer")
        A[(i,k)]  = pulp.LpVariable(f"A_{i}_{k}", lowBound=0, cat="Integer")
        LA[(i,k)] = pulp.LpVariable(f"LA_{i}_{k}", lowBound=0, cat="Integer")

# =============================================
# 约束（核心）
# =============================================

# 1) 初始 V_{i,1} = x_i
for i in range(N):
    model += Vi[(i,1)] == xi[i]

# 2) 递推 V
for i in range(N):
    for k in range(2, K+1):
        model += Vi[(i,k)] == \
            Vi[(i,k-1)] + \
            pulp.lpSum([R[j,i,k-1] for j in range(N)]) - \
            pulp.lpSum([B[i,j,k-1] for j in range(N)])

# 3) A = V + arrivals
for i in range(N):
    for k in range(1, K+1):
        model += A[(i,k)] == Vi[(i,k)] + pulp.lpSum([R[j,i,k] for j in range(N)])

# 4) L_i,k = y_i - V_i,k
for i in range(N):
    for k in range(1, K+1):
        model += Li[(i,k)] == yi[i] - Vi[(i,k)]

# 5) LA = free slots + departures（注意方向）
for i in range(N):
    for k in range(1, K+1):
        model += LA[(i,k)] == Li[(i,k)] + pulp.lpSum([B[i,j,k] for j in range(N)])

# 6) 可行性约束
#   (9) A_i,k >= 出发需求
for i in range(N):
    for k in range(1, K+1):
        model += A[(i,k)] >= pulp.lpSum([B[i,j,k] for j in range(N)])

#   (10) LA_i,k >= 到达需求
for i in range(N):
    for k in range(1, K+1):
        model += LA[(i,k)] >= pulp.lpSum([R[j,i,k] for j in range(N)])

# 7) x_i <= y_i
for i in range(N):
    model += xi[i] <= yi[i]

# 8) 容量上界
for i in range(N):
    model += yi[i] <= MAX_PARK

# ================================
# 求解
# ================================
solver = pulp.PULP_CBC_CMD(msg=True)
model.solve(solver)

print("Status:", pulp.LpStatus[model.status])
print("Objective =", pulp.value(model.objective))

# 结果输出
res = pd.DataFrame({
    "station_id": stations,
    "x_i": [int(pulp.value(xi[i])) for i in range(N)],
    "y_i": [int(pulp.value(yi[i])) for i in range(N)]
})
res.to_csv("result_capacity.csv", index=False)
print(res.head())
print("已保存 result_capacity.csv")