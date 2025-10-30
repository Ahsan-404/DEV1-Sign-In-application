import requests

url = "https://fastapi-app-cr0h.onrender.com/add-user/"


username = input("Enter username: ")
password = input("Enter password: ")

data = {
    "username" : username,
    "password" : password
}

response = requests.post(url, json=data)
print(response.json())