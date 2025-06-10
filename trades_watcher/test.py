import requests

# Check if order exists
resp = requests.post("http://127.0.0.1:8000/order_exists", json={
    "symbol": "WEED.TO",
    "side": "B",
    "price": 2
})
print(resp.json())

# Get traded volume
# resp = requests.get("http://localhost:8000/traded_volume", params={"symbol": "TD.TO"})
# print(resp.json())