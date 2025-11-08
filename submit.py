import requests
import os
import time

os.system("cls" if os.name == "nt" else "clear")

# redeployed
# redeploy

BASE_URL = "https://fastapi-app-cr0h.onrender.com"

print("Welcome! Choose an option:")
print("1. Sign up")
print("2. Log in")
choice = input("Enter 1 or 2: ")

username = input("Enter username: ")
password = input("Enter password: ")

data = {
    "username": username,
    "password": password
}

if choice == "1":
    endpoint = "/add-user/"
elif choice == "2":
    endpoint = "/login/"
else:
    print("❌ Invalid choice.")
    exit()

response = requests.post(BASE_URL + endpoint, json=data)

if response.status_code == 200:
    try:
        print("✅ Success:", response.json()["message"])
    except ValueError:
        print("✅ Success, but no message returned.")
else:
    try:
        error = response.json().get("detail", "Unknown error")
    except ValueError:
        error = response.text  # fallback if not JSON
    print("❌ Error:", error)
    exit()

# Extract access token
token = response.json().get("access_token")

# --- Chat Loop ---
print("\nYou can now send messages. Type 'exit' to quit.")

time.sleep(2)
os.system("cls" if os.name == "nt" else "clear")

while True:
    msg_content = input("Message: ")
    os.system("cls" if os.name == "nt" else "clear")
    if msg_content.lower() == "exit":
        break

    # Send message
    msg_data = {"token": token, "content": msg_content}
    resp = requests.post(BASE_URL + "/chat/", json=msg_data)
    
    if resp.status_code == 200:
        print("✅ Message sent!")
    else:
        try:
            error = resp.json().get("detail", "Unknown error")
        except ValueError:
            error = resp.text
        print("❌ Error:", error)
    
    # Fetch latest 50 messages
    resp = requests.get(BASE_URL + "/chat/")
    if resp.status_code == 200:
        for m in resp.json():
            print(f"[{m['timestamp']}] {m['username']}: {m['content']}")
    else:
        print("❌ Could not fetch messages")
