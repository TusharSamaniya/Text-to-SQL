# test_endpoint.py — send a real question to the running server.
# (Not a unit test of internals - a live HTTP call, like curl but no quote fuss.)
import requests

question = "What is the total revenue from payments?"
resp = requests.post(
    "http://127.0.0.1:5000/api/ask",
    json={"question": question},
)
print("Status:", resp.status_code)
print(resp.json())