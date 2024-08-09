import requests
import base64

url = 'http://127.0.0.1:20162/upload'

data = {
    'data': '2024-08-06T14:00:00',
    'opis': 'Przykładowy opis',
    'zdjecie': base64.b64encode(open('testimage.jpg', 'rb').read()).decode('utf-8'),
    'latitude': 52.2296756,
    'longitude': 21.0122287
}

response = requests.post(url, json=data)
print(response.json())
