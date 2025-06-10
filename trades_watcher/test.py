import requests

# Check if order exists
resp = requests.post("http://127.0.0.1:8000/order_exists", json={
    "symbol": "TD.TO",
    "side": "B",
    "price": 95.70
})
print(resp.json()['exists'])

# Get traded volume
# resp = requests.get("http://localhost:8000/traded_volume", params={"symbol": "TD.TO"})
# print(resp.json())