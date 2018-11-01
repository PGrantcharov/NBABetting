import pandas as pd
import numpy as np
import datetime as dt


df = pd.read_csv("../Data/combined.csv")
df.dropna(axis=0, how="any", inplace=True)
df = df.reset_index().drop(columns=["Unnamed: 0"])

year = "2007"
for i in range(len(df)):
    try:
        if (df.iloc[i+1, 1] - df.iloc[i, 1]) > 200:  # this checks when there's a jump in months since last game
            year = str(int(year) + 1)
    except IndexError:
        pass
    df.iloc[i, 1] = str(df.iloc[i, 1]) + year

fucked_dates = []
for i in range(len(df)):
    try:
        df.iloc[i, 1] = dt.datetime.strptime(df.iloc[i, 1], "%m%d%Y").date()
    except ValueError:
        fucked_dates.append(i)

# NEED TO FIX THESE DATES

# run when we're done
# df.to_csv("../Data/cleaned.csv")
