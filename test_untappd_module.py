import untappd
import sys

query = "Alesong Brewing Rhino Suit"
print(f"Searching for: {query}")
result = untappd.search_beer(query)

if result:
    print("Success!")
    print(result)
else:
    print("Failed to find result.")
    sys.exit(1)
