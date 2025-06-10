import requests

# Check if order exists
resp = requests.post("http://localhost:8000/order_exists", json={
    "symbol": "TD.TO",
    "side": "B",
    "price": 95.70
})
print(resp.json())

# Get traded volume
resp = requests.get("http://localhost:8000/traded_volume", params={"symbol": "TD.TO"})
print(resp.json())