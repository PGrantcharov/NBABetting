import pandas as pd
import os

file_names = os.listdir("../Data/Raw")
file_names.sort()

dfs = []
for i in range(len(file_names)):
    dfs.append(pd.ExcelFile("../Data/Raw/" + file_names[i]).parse("Sheet1"))

combined = pd.concat(dfs)

combined.to_csv("../Data/combined.csv")
