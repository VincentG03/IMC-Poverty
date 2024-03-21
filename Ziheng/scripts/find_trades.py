# takes a file and reads it 
# reads the log and then converts it into a pandas for printing later
from pprint import pprint
import json
import pandas as pd

def convert_to_pandas(file_name):
    with open(file_name, "r") as f:
        stuff = f.read()

    lst = stuff.split("Trade History:")
    dic = json.loads(lst[1])

    i = 0
    df = pd.DataFrame({"product": [], "timestamp": [], "position": [], "price": []})
    for d in dic:
        if d["buyer"] == "SUBMISSION":
            df.loc[len(df)] = ({"product": d["symbol"], "timestamp": d["timestamp"], "position": d["quantity"], "price": d["price"]})
        if d["seller"] == "SUBMISSION":
            df.loc[len(df)] = ({"product": d["symbol"], "timestamp": d["timestamp"], "position": -d["quantity"], "price": d["price"]})
            
    return df

# print(convert_to_pandas("Ziheng/scripts/testMM.log"))
