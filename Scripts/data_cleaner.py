import pandas as pd
import numpy as np
import datetime as dt


df = pd.read_csv("../Data/combined.csv")
df.dropna(axis=0, how="any", inplace=True)
df = df.reset_index(drop=True).drop(columns=["Unnamed: 0", "Rot"])

# Adds season year (07-08 season would just add 2007 for all) to all dates
year = "2007"
len_last = 4
for i in range(len(df)):
    if len(str(df.ix[i, "Date"])) > len_last:  # this checks when there's a jump in months since last game
        year = str(int(year) + 1)
    len_last = len(str(df.ix[i, "Date"]))
    df.ix[i, "Date"] = str(df.ix[i, "Date"]) + year


# Converts to dates to date object; converts feb 29 days to feb 28 as these were only errors
for i in range(len(df)):
    try:
        df.ix[i, "Date"] = dt.datetime.strptime(df.ix[i, "Date"], "%m%d%Y").date()
    except ValueError:
        df.ix[i, "Date"] = str(int(df.ix[i, "Date"]) - 10000)
        df.ix[i, "Date"] = dt.datetime.strptime(df.ix[i, "Date"], "%m%d%Y").date()


# run when we're done cleaning and tidying
# df.to_csv("../Data/cleaned.csv")
