import requests

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
    print("✅ Success:", response.json()["message"])
else:
    print("❌ Error:", response.json().get("detail", "Unknown error"))
