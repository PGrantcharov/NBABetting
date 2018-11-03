import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns

df = pd.read_csv("../Data/combined.csv")
df = df.reset_index(drop=True).drop(columns=["Unnamed: 0", "Rot"])

# Make spelling consistent; replace NewJersey --> Brooklyn
df = df.replace(to_replace="NewJersey", value="Brooklyn")
df = df.replace(to_replace="Oklahoma City", value="OklahomaCity")
df = df.replace(to_replace="LA Clippers", value="LAClippers")


# fix detroit v. phoenix game scores; bad entry fixes
df.ix[[2916, 2917], ["1st", "2nd"]] = [[23, 23], [31, 30]]
df.ix[1974, "Open"] = 197.5
df.ix[11192, "2H"] = np.nan
df.ix[23520, 'Open'] = 195.5


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


# MAKE TIDY DATA FRAME
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

# Removes/fixes a few outliers
tidy.iloc[:, 3:11] = tidy.iloc[:, 3:11][tidy.iloc[:, 3:11] < 70]
tidy.iloc[:, 3:11] = tidy.iloc[:, 3:11][tidy.iloc[:, 3:11] > 0]
tidy.OUOpen = tidy.OUOpen[tidy.OUOpen > 100]
tidy = tidy.reset_index(drop=True)
tidy.iloc[:, 3:] = tidy.iloc[:, 3:].astype(float)
tidy.OUOpen[tidy.OUOpen == tidy.OUOpen.min()] = tidy.OUClose[tidy.OUOpen == tidy.OUOpen.min()]
tidy.ix[5598, 'OU2H'] = round(tidy[tidy.OUClose.between(197, 198)].OU2H.mean()*2)/2
tidy.dropna(axis=0, how='any', inplace=True)

tidy.ix[11958, 'VF'] = tidy.ix[11958, ['V1', 'V2', 'V3', 'V4']].sum()
tidy.ix[11958, 'HF'] = tidy.ix[11958, ['H1', 'H2', 'H3', 'H4']].sum()

tidy.to_csv("../Data/tidy.csv")


# Quick graphs to check for outliers:
tidy.ix[:, 3:11].plot(kind='box')  # Quarter Scores
tidy.ix[:, 11:13].plot(kind='box')  # Final Scores
tidy.ix[:, 13:15].plot(kind='box')  # OUs
tidy.ix[:, 15:19].plot(kind='box')  # Spreads
tidy.ix[:, 19:21].plot(kind='box')  # Money lines
tidy.ix[:, 21].plot(kind='box')  # OU second half
tidy.ix[:, 22:].plot(kind='box')  # Spreads second half

