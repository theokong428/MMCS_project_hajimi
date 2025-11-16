import pandas as pd

# 读取数据
df = pd.read_csv("merged_2018_2021.csv")

# =========================
# 1. 时间字段自动转换
# =========================
df['started_at'] = pd.to_datetime(df['started_at'], utc=True, errors='coerce')
df['ended_at'] = pd.to_datetime(df['ended_at'], utc=True, errors='coerce')

# 删除无法解析的时间行
df = df.dropna(subset=['started_at', 'ended_at'])

# =========================
# 2. 清洗异常值
# =========================

#去掉相同站点数据
df = df[df['start_station_id'] != df['end_station_id']]

#小于60s可能是车有问题，大于十二小时则认为忘了还车，不能用这个去预估需求
df = df[(df['duration'] > 60) & (df['duration'] < 12*3600)]

# =========================
# 3. 提取日期与小时
# =========================
df['date'] = df['started_at'].dt.date
df['hour'] = df['started_at'].dt.hour
df['end_hour'] = df['ended_at'].dt.ceil('h').dt.hour
# 将 date 转为 datetime（防止是 object）
df['date'] = pd.to_datetime(df['date'])

# 创建工作日标签：0=周一, 6=周日
df['is_weekend'] = df['date'].dt.weekday >= 5

# 转为文字标签（更适合建模）
df['day_type'] = df['is_weekend'].map({False: '1', True: '0'})
# =========================
# 4. 构造每天每小时 OD 流量
# =========================
od = df.groupby(
    ['date', 'hour', 'end_hour','start_station_id', 'end_station_id','day_type']
).size().reset_index(name='trips')

# 保存结果
od.to_csv("od.csv", index=False)

od.head()