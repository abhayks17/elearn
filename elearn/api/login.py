import requests

url = "http://localhost:8002/api/method/login"
payload = {
    "usr": "athul@gmail.com",
    "pwd": "abhay123"
}

response = requests.post(url, data=payload)
print(response.json())
