import pandas as pd
import numpy as np

df = pd.read_csv("merged_2018_2021.csv")

# 2. analyse time
df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
df['ended_at'] = pd.to_datetime(df['ended_at'], errors='coerce')

df = df[df['started_at'].notna() & df['ended_at'].notna()]

# 3. hour feature
df['time_start'] = df['started_at'].dt.hour
df['time_end'] = df['ended_at'].dt.hour

df['time_start_end'] = (df['time_start'] + 1) % 24
df['time_end_end'] = (df['time_end'] + 1) % 24

# 4. date
df['date_start'] = pd.to_datetime(df['started_at'].dt.date)
df['date_end'] = pd.to_datetime(df['ended_at'].dt.date)

# 5. holiday
holidays = pd.to_datetime([
    "2018-01-01","2018-03-30","2018-04-02","2018-05-07","2018-05-28","2018-08-27","2018-12-25","2018-12-26",
    "2019-01-01","2019-04-19","2019-04-22","2019-05-06","2019-05-27","2019-08-26","2019-12-25","2019-12-26",
    "2020-01-01","2020-04-10","2020-04-13","2020-05-08","2020-05-25","2020-08-31","2020-12-25","2020-12-28",
    "2021-01-01","2021-04-02","2021-04-05","2021-05-03","2021-05-31","2021-08-30"
])

# 6. station
start_stations = df[['start_station_id','start_station_latitude','start_station_longitude']].drop_duplicates()
start_stations = start_stations.rename(columns={
    'start_station_id':'station_id',
    'start_station_latitude':'latitude',
    'start_station_longitude':'longitude'
})

end_stations = df[['end_station_id','end_station_latitude','end_station_longitude']].drop_duplicates()
end_stations = end_stations.rename(columns={
    'end_station_id':'station_id',
    'end_station_latitude':'latitude',
    'end_station_longitude':'longitude'
})

stations = pd.concat([start_stations, end_stations]).drop_duplicates(subset='station_id').reset_index(drop=True)

# 7. date*hour%station
dates = pd.date_range(df['date_start'].min(), df['date_end'].max(), freq='D')
hours = np.arange(0,24)

station_time_df = pd.MultiIndex.from_product(
    [stations['station_id'], dates, hours],
    names=['station_id','date','time_start']
).to_frame(index=False)

station_time_df['time_end'] = (station_time_df['time_start'] + 1) % 24
station_time_df = station_time_df.merge(stations, on='station_id', how='left')

# 8. week_type & workday
station_time_df['week_type'] = station_time_df['date'].dt.day_name()
station_time_df['workday'] = np.where(
    (station_time_df['week_type'].isin(['Saturday','Sunday'])) | (station_time_df['date'].isin(holidays)),
    0, 1
)

# 9. borrow demand
borrow = df.groupby(['start_station_id','date_start','time_start']).size().reset_index(name='borrow_demand')
borrow = borrow.rename(columns={'start_station_id':'station_id','date_start':'date'})
borrow['date'] = pd.to_datetime(borrow['date'])

# 10. return demand
return_ = df.groupby(['end_station_id','date_end','time_end']).size().reset_index(name='return_demand')
return_ = return_.rename(columns={'end_station_id':'station_id','date_end':'date','time_end':'time_start'})
return_['date'] = pd.to_datetime(return_['date'])

# 11. combine borrow/return
result = station_time_df.merge(borrow, on=['station_id','date','time_start'], how='left')
result = result.merge(return_[['station_id','date','time_start','return_demand']],
                      on=['station_id','date','time_start'], how='left')

# 12. missing value
result['borrow_demand'] = result['borrow_demand'].fillna(0)
result['return_demand'] = result['return_demand'].fillna(0)

result = result[['station_id','latitude','longitude','date','week_type','workday',
                 'time_start','time_end','borrow_demand','return_demand']]

result.to_csv("station_record.csv", index=False)
print(" processed and generate station_record.csv")
