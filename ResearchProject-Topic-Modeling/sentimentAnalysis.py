import json
import pandas as pd


data = pd.read_csv("static/CSV/staticData-global-warming.csv")

# LIST FORMAT
sentAnalysis = data.Analysis.value_counts().tolist()
print(sentAnalysis)
print(sentAnalysis[0])
print(sentAnalysis[1])
print(sentAnalysis[2])

# JSON FORMAT
sentAnalysis = json.loads(data.Analysis.value_counts().to_json())
print(sentAnalysis)
print(sentAnalysis['Positive'])
print(sentAnalysis['Neutral'])
print(sentAnalysis['Negative'])
