import json

jsonfl="./data/crime_rate.json"

with open(jsonfl, "r", encoding="utf-8-sig") as f:
                ans= json.load(f)["DataList"]
                relevant=[]
                for item in ans:
                        if "Sukhbaatar" in item["SCR_ENG"]:
                                relevant.append(item)
                                