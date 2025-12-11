import requests
import json

APP_ID = "9WBO4RQ3HO"
API_KEY = "1d347324d67ec472bb7132c66aead485"
ALGOLIA_URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/beer/query"
HEADERS = {
    "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser (lite)",
    "x-algolia-application-id": APP_ID,
    "x-algolia-api-key": API_KEY,
}

query = "Alesong Brewing Rhino Suit"
data = {"params": f"query={query}&hitsPerPage=1"}
response = requests.post(ALGOLIA_URL, headers=HEADERS, json=data)
if response.status_code == 200:
    res = response.json()
    if res['hits']:
        print("Keys available:", res['hits'][0].keys())
        print("Slug:", res['hits'][0].get('beer_slug'))
        print("Bid:", res['hits'][0].get('bid'))
