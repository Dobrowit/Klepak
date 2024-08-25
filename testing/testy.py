#########################
## !! ZAKTUALIZOWAĆ !! ##
#########################
import unittest
import json
import os
from base64 import b64encode
from io import BytesIO
from klepak import app, load_data, save_data, DATA_DIR, DATA_FILE

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        # Usuwanie plików danych po każdym teście
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        if os.path.exists(DATA_DIR):
            for file in os.listdir(DATA_DIR):
                os.remove(os.path.join(DATA_DIR, file))
            os.rmdir(DATA_DIR)

    def test_load_data_empty(self):
        data = load_data()
        self.assertEqual(data, [])

    def test_save_and_load_data(self):
        data = [{'data': '2021-08-06', 'opis': 'Test', 'zdjecie': 'test.jpg', 'latitude': 54.7578, 'longitude': 17.5610}]
        save_data(data)
        loaded_data = load_data()
        self.assertEqual(data, loaded_data)

    def test_upload_endpoint(self):
        image = BytesIO()
        image.write(b'some image data')
        image.seek(0)
        image_base64 = b64encode(image.read()).decode('utf-8')

        response = self.app.post('/upload', json={
            'data': '2021-08-06',
            'opis': 'Test',
            'zdjecie': image_base64,
            'latitude': 54.7578,
            'longitude': 17.5610
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dane zapisane pomyślnie', response.get_json()['message'])

    def test_get_data_endpoint(self):
        save_data([{'data': '2021-08-06', 'opis': 'Test', 'zdjecie': 'test.jpg', 'latitude': 54.7578, 'longitude': 17.5610}])
        response = self.app.get('/data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_map_view(self):
        save_data([{'data': '2021-08-06', 'opis': 'Test', 'zdjecie': 'test.jpg', 'latitude': 54.7578, 'longitude': 17.5610}])
        response = self.app.get('/map')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<html>', response.get_data(as_text=True))

    def test_table_view(self):
        save_data([{'data': '2021-08-06', 'opis': 'Test', 'zdjecie': 'test.jpg', 'latitude': 54.7578, 'longitude': 17.5610}])
        response = self.app.get('/table')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<table', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
