
## Files and Directory Overview (Recommended Structure)

```text
project：
├── data/
│   ├── merged_2018_2021.csv（too large to commit）   #output from Step1_data_preprocess.ipynb, combine raw data ,
│   ├── od.csv                                       #output from Step1_data_preprocess.ipynb, count each day's trip hour by hour,
│   ├── od_hourly_zip_poisson_daytype_1.csv          #output from Step1_data_preprocess.ipynb, predict demand for modeling,
│   ├── Minlimit_capacity_daytype_1.csv              #output from Step2_Capacity.ipynb.ipynb,  result from capacity model,
│   ├── station_daily_balance_daytype_1.csv          #outpit from Step3_Reblancing.ipynb, count the situation at the end of day
│   ├── station_tasks.csv                            #output from Step3_Reblancing.ipynb, reorder data
│   ├── distance_matrix_int_km.csv                   #output from Step4_Test.ipynb, record distance
│   └── od_test_10days.csv                           #output from Step4_Test.ipynb, as test example
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
