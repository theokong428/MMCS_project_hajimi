
## Files and Directory Overview (Recommended Structure)

```text
project：
├── data/
│   ├── merged_2018_2021.csv
│   ├── od.csv
│   ├── od_hourly_zip_poisson_daytype_0.csv
│   ├── od_hourly_zip_poisson_daytype_1.csv
│   ├── Minlimit_capacity_daytype_0.csv
│   ├── Minlimit_capacity_daytype_1.csv
│   ├── od_test_10days.csv
│   ├── station_daily_balance_daytype_1.csv
│   ├── station_tasks.csv
│   └── distance_matrix_int_km.csv
│
│
│
├── notebooks/
│   ├── Step1_data_preprocess.ipynb      # Data cleaning and demand prediction by ZIP
│   ├── Step2_Capacity.ipynb             # Station capacity modeling
│   ├── Step3_Reblancing.ipynb           # Reorder data and GA-based model
│   ├── Step4_Test.ipynb                 # Simulate capacity performance and price testing
│   └── Step5_Visualization.ipynb        # Mapping, charts, and result visualization
│
│
└── README.md
