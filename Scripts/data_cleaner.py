import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns


df = pd.read_csv("../Data/combined.csv")
df.dropna(axis=0, how="any", inplace=True)
df = df.reset_index(drop=True).drop(columns=["Unnamed: 0", "Rot"])


# Make spelling consistent; replace NewJersey --> Brooklyn
df = df.replace(to_replace="NewJersey", value="Brooklyn")
df = df.replace(to_replace="Oklahoma City", value="OklahomaCity")
df = df.replace(to_replace="LA Clippers", value="LAClippers")

'''
# shows where the outliers are
sns.catplot(y='1st', data=df, kind="box")
sns.catplot(y='2nd', data=df, kind="box")
sns.catplot(y='3rd', data=df, kind="box")
sns.catplot(y='4th', data=df, kind="box")
'''

# Removes a few outliers
df = df[df['1st'] < 70]
df = df[df['2nd'] > 0]
df = df.reset_index(drop=True)

# fix detroit v. phoenix game scores; bad entry fixes
df.ix[[2916, 2917], ["1st", "2nd"]] = [[23, 23], [31, 30]]
df.ix[1974, "Open"] = 197.5
df.ix[11192, "2H"] = np.nan


# replace all pk odds (i.e. 50/50 outcomes) with 0 so we can make last four columns integers
df = df.replace(to_replace=["pk", "PK"], value=0)
df = df.replace(to_replace="NL", value=np.nan)


# make last few columns numeric
df[["Open", "Close", "ML", "2H"]] = df[["Open", "Close", "ML", "2H"]].astype(float)


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


# Make tidy data frame

# columns of new data frame that has one game per row
tidy = pd.DataFrame(columns=["Date", "V", "H", "V1", "V2", "V3", "V4", "H1", "H2", "H3", "H4", "VF", "HF",
                             "OUOpen", "OUClose", "VSpreadOpen", "HSpreadOpen", "VSpreadClose", "HSpreadClose",
                             "VMoney", "HMoney", "OU2H", "VSpread2H", "HSpread2H"])

for i in range(int(len(df)/2)-1):
    # only fills in until HF
    row = [df['Date'][i*2], df['Team'][i*2], df['Team'][i*2+1], df['1st'][i*2], df['2nd'][i*2], df['3rd'][i*2],
           df['4th'][i*2], df['1st'][i*2+1], df['2nd'][i*2+1], df['3rd'][i*2+1], df['4th'][i*2+1], df['Final'][i*2],
           df['Final'][i*2+1]]

    # Adds OUOpen
    if df["Open"][i*2] > df["Open"][i*2+1]:
        row.append(df["Open"][i*2])
    else:
        row.append(df["Open"][i*2+1])

    # Adds OUClose
    if df["Close"][i*2] > df["Close"][i*2+1]:
        row.append(df["Close"][i*2])
    else:
        row.append(df["Close"][i*2+1])

    # Adds VSpreadOpen and HSpreadOpen
    if df["Open"][i*2] > df["Open"][i*2+1]:
        row.append(df["Open"][i*2+1]*(-1))
        row.append(df["Open"][i*2+1])
    else:
        row.append(df["Open"][i*2])
        row.append(df["Open"][i*2]*(-1))

    # Adds VSpreadClose and HSpreadClose
    if df["Close"][i*2] > df["Close"][i*2+1]:
        row.append(df["Close"][i*2+1]*(-1))
        row.append(df["Close"][i*2+1])
    else:
        row.append(df["Close"][i*2])
        row.append(df["Close"][i*2]*(-1))

    # VMoney and HMoney
    row.append(df["ML"][i*2])
    row.append(df["ML"][i*2+1])

    # OU2H
    if df["2H"][i*2] > df["2H"][i*2+1]:
        row.append(df["2H"][i*2])
        row.append(df["2H"][i*2+1]*(-1))
        row.append(df["2H"][i*2+1])
    else:
        row.append(df["2H"][i*2+1])
        row.append(df["2H"][i*2])
        row.append(df["2H"][i*2]*(-1))

    tidy.loc[i] = row

df.to_csv("../Data/tidy.csv")

