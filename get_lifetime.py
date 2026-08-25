import pandas as pd
from pathlib import Path


folder = Path('C:/Users/sures/Documents/DA Projects/IowaStateCells/capacity_fade/Release 1.0')

files = list(folder.glob("*.csv"))

outList = []

for file in files:
    fileName = Path(file).stem
    df = pd.read_csv(file)
    df = df[df['Capacity'] > 0.20]

    lifetime = max(df['Time'])

    outDict = {
        'ID': fileName,
        'Lifetime': lifetime
    }

    outList.append(outDict)

groupData = pd.DataFrame(outList)


lifetimeDict = dict(zip(groupData['ID'], groupData['Lifetime']))


def lifetime(cellId):
    return lifetimeDict[cellId]