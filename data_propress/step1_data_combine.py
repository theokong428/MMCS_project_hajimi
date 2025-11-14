import pandas as pd
import glob

file_list = sorted(glob.glob('data_propress/raw_data/[2][0][1][8-9]_??.csv') + glob.glob('data_propress/raw_data/[2][0][2][0-1]_??.csv'))
print("Total number：", len(file_list))

# combie(clolumn)
df_all = pd.concat([pd.read_csv(f) for f in file_list], ignore_index=True)

df_all.to_csv('merged_2018_2021.csv', index=False)

print("output：merged_2018_2021.csv")
