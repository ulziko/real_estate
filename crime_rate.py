import requests
import json

url = "https://opendata.1212.mn/api/Data?type=json"

payload = {
    "tbl_id": "DT_NSO_2300_003V1", 
    "Period": ["2025", "2024","2023", "2022", "2021"], 
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    try:
        data = response.json()
        
        with open("./data/crime_rate.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Data saved to nso_data.json")
        
    except ValueError:
        print("Response content is not valid JSON.")
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response content:", response.text)