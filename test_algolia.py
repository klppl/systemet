import requests
import json

APP_ID = "DT1687HS28"
API_KEY = "219af4690586a51d8d18f8e87498906a" # This is another key often found, let's try the one from the blog post... wait the blog post hid it.
# Actually the one in my thought trace earlier: 29849509f6b57912d09df4424759685a
API_KEY = "29849509f6b57912d09df4424759685a" 

headers = {
    "X-Algolia-Application-Id": APP_ID,
    "X-Algolia-API-Key": API_KEY,
}

url = f"https://{APP_ID}-dsn.algolia.net/1/indexes/beer/query"

query = "Norrlands Guld Export"

data = {
    "params": f"query={query}&hitsPerPage=1"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(e)
