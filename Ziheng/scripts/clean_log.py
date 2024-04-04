from pprint import pprint
import json
import pandas as pd

def clean_log(file_name):
    with open(file_name, "r") as f:
        stuff = f.read()

    lst = stuff.split("Activities log:")


    with open("Jonathan/6010_profit_CLEAN.log", "w") as f:
        f.write(lst[0].replace('\\n', '\n'))


print(clean_log("Jonathan/6010_profit.log"))