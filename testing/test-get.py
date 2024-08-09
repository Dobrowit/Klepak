import requests

url = 'http://127.0.0.1:20162/data'

response = requests.get(url)
print(response.json())
