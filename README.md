# Shared Bike Scheme Project



## 文件与目录总览（建议结构）

```text
project/
├── data/
│   ├── merged_2018_2021.csv
│   ├── od.csv
│   ├── od_hourly_zip_poisson_daytype_0.csv
│   ├── od_hourly_zip_poisson_daytype_1.csv
│   ├── Minlimit_capacity_daytype_1.csv
│   ├── od_test_10days.csv
│   ├── station_daily_balance_daytype_1.csv
│   ├── station_tasks.csv
│   └── distance_matrix_int_km.csv
│
├── notebooks/
│   ├── 01_data_preprocess.ipynb
│   ├── 02_demand_zip_poisson.ipynb
│   ├── 03_capacity_ilp.ipynb
│   ├── 04_evaluation_simulation.ipynb
│   ├── 05_rebalance_task_building.ipynb
│   ├── 06_vrp_ga_rebalancing.ipynb
│   └── 07_revenue_analysis.ipynb
│
├── src/
│   ├── 01_build_od.py
│   ├── 02_zip_demand.py
│   ├── 03_capacity_model.py
│   ├── 04_sample_test_days.py
│   ├── 05_simulate_capacity_performance.py
│   ├── 06_station_balance.py
│   ├── 07_build_station_tasks.py
│   ├── 08_vrp_ga_rebalancing.py
│   └── 09_daily_revenue.py
│
└── README.md
