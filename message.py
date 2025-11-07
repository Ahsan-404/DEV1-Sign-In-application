import requests

BASE_URL = "https://fastapi-app-cr0h.onrender.com"

# Send a message
username = input("Username: ")
msg = input("Message: ")

resp = requests.post(BASE_URL + "/chat/", json={"username": username, "content": msg})
print(resp.json())

# Get all messages
resp = requests.get(BASE_URL + "/chat/")
for m in resp.json():
    print(f"[{m['timestamp']}] {m['username']}: {m['content']}")
