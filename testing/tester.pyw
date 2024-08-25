import requests
import json
import random
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "tester.ui"
RESOURCE_PATHS = [PROJECT_PATH]

def generate_data():
    # Generowanie losowych danych
    category = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 99, 444,])
    user = random.choice(["d4fb8586-101f-4dff-a91e-2488b8214ba3", "9389f8dd-18f8-444a-8dd7-4c815f349a6f", "", "uhbubuy7689"])
    message = random.choice(["","Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ut consectetur est. In dictum egestas erat vel convallis. Curabitur vestibulum dui a dui faucibus, eget egestas est consequat. Praesent auctor purus et pharetra porttitor. Curabitur sed consectetur ante. Donec tincidunt aliquet euismod. Morbi tristique pellentesque ipsum, eu faucibus nunc pharetra vel. Integer cursus iaculis felis eu tempor. Phasellus et fringilla lectus, et convallis tortor. Integer et dictum tortor. Nam malesuada erat lorem, at accumsan quam blandit vitae."])
    latitude = random.uniform(54.74, 54.77)
    longitude = random.uniform(17.53, 17.57)
    
    # Tworzenie słownika
    data = {
        "Category": category,
        "Latitude": latitude,
        "Longitude": longitude,
        "UserId": user,
        "Message": message,
        "Base64Image": "/9j/4AAQSkZJRgABAQEBLAEsAAD//gATQ3JlYXRlZCB3aXRoIEdJTVD/4gKwSUNDX1BST0ZJTEUAAQEAAAKgbGNtcwRAAABtbnRyUkdCIFhZWiAH6AAIABcAEAAmACRhY3NwTVNGVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWxjbXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1kZXNjAAABIAAAAEBjcHJ0AAABYAAAADZ3dHB0AAABmAAAABRjaGFkAAABrAAAACxyWFlaAAAB2AAAABRiWFlaAAAB7AAAABRnWFlaAAACAAAAABRyVFJDAAACFAAAACBnVFJDAAACFAAAACBiVFJDAAACFAAAACBjaHJtAAACNAAAACRkbW5kAAACWAAAACRkbWRkAAACfAAAACRtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACQAAAAcAEcASQBNAFAAIABiAHUAaQBsAHQALQBpAG4AIABzAFIARwBCbWx1YwAAAAAAAAABAAAADGVuVVMAAAAaAAAAHABQAHUAYgBsAGkAYwAgAEQAbwBtAGEAaQBuAABYWVogAAAAAAAA9tYAAQAAAADTLXNmMzIAAAAAAAEMQgAABd7///MlAAAHkwAA/ZD///uh///9ogAAA9wAAMBuWFlaIAAAAAAAAG+gAAA49QAAA5BYWVogAAAAAAAAJJ8AAA+EAAC2xFhZWiAAAAAAAABilwAAt4cAABjZcGFyYQAAAAAAAwAAAAJmZgAA8qcAAA1ZAAAT0AAACltjaHJtAAAAAAADAAAAAKPXAABUfAAATM0AAJmaAAAmZwAAD1xtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAEcASQBNAFBtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEL/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2P/2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2P/wgARCABkAGQDAREAAhEBAxEB/8QAFwABAQEBAAAAAAAAAAAAAAAAAAECA//EABgBAQEBAQEAAAAAAAAAAAAAAAABAgME/9oADAMBAAIQAxAAAAGertVAC2hQAC5nOlFIAUgBaXExotuJN0kgMmgVpd888rWltpEmE0ZNBaq9eeeFt01qoykxJaBRW7enPPDV1q6qRmSZk1UAXTa9MTiXdtSTMTJoEMS9b0XacsG6SRkCkMRF666G65QxJUqADMZN3WrutnKEmcxAEFtqGtXpWjlJICrEIURDWrurJziVpaSTNUQiVrV0WTmtrRYwkWhJC3VaH//EABwQAAEEAwEAAAAAAAAAAAAAABEAASAwEEBBUP/aAAgBAQABBQLd7A2itrWo7BtB00jE0DBRwPM//8QAGhEAAwEBAQEAAAAAAAAAAAAAAAEwESBAEP/aAAgBAwEBPwHy6aab6lVVVVRCohUQqqi7fS+//8QAFBEBAAAAAAAAAAAAAAAAAAAAcP/aAAgBAgEBPwEp/8QAFBABAAAAAAAAAAAAAAAAAAAAcP/aAAgBAQAGPwIp/8QAHRAAAgIDAQEBAAAAAAAAAAAAAREAIBAhMDFAUf/aAAgBAQABPyHmouwOXyBgUBLwlRgU9cBQ+T1dQGoN0J3lQhGAsXKBuhDmxU4fxE4NVO4Y2I0aImgfSOoz/9oADAMBAAIAAwAAABDrfwg20bMJItuUOWP8/oK+RBwh5XGt8S78AxJSx+WlOcjPq3fZ3U80BsVgFWdPJw0Ivd7/ANka6t6fuLVOqFaAf//EABsRAAMBAQEBAQAAAAAAAAAAAAABESAQITAx/9oACAEDAQE/EKUpSlKVHh525pSlwEKXVKUpRCXhSi4+UuS/BCEhjHuhCEMb0uUJC42PS5QuUbwsi63lfAZCD4tj4kQZCDRBYQSIPD4guoWE48v/xAAcEQACAgMBAQAAAAAAAAAAAAABEQAgEDBAMVD/2gAIAQIBAT8Q+E9bwtYqLmCo0ChodBgoZ5HUmKCyw44osjpHB//EAB8QAQACAgIDAQEAAAAAAAAAAAEAERAgITFBUXGBkf/aAAgBAQABPxDFSiUSiUSiUSiUSmBCVvcuXLwDCW8nvW/o2DFKLui8qIvGPpkyIMOO75HQwEEMM7Pk7vkckMEJwXi4EYx5EiHI8SoxidVhgi5/s5COrKCh5l1vBDNSvMtfUA98aIO2XcQNX49wgohlgOxF8Mr2k+EfhBHI/sod8xhoXAaVHBDQJUdHA0Mujq//2Q=="
    }
    
    return data

class AppUI:
    def __init__(self, master=None, on_first_object_cb=None):
        self.builder = pygubu.Builder(on_first_object=on_first_object_cb)
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object("toplevel1", master)
        self.builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def btn_gen(self):
        data = generate_data()
        data = json.dumps(data, indent=0)

        url_entry_o = self.builder.get_object('url_entry')
        url_entry_o.delete(0, tk.END)
        url_entry_o.insert(0, "https://klepak.cytr.us/upload")

        json_text_o = self.builder.get_object('json_text')
        json_text_o.delete(1.0, tk.END)
        json_text_o.insert(tk.END, data)

    def btn_get(self):
        url = self.builder.get_object('url_entry').get()
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            self.display_response(response)
        except requests.RequestException as e:
            self.display_error(str(e))

    def btn_post(self):
        url = self.builder.get_object('url_entry').get()
        try:
            data = json.loads(self.builder.get_object('json_text').get("1.0", tk.END))
            response = requests.post(url, json=data)
            self.display_response(response)
        except json.JSONDecodeError:
            self.display_error("Invalid JSON data")
        except requests.RequestException as e:
            self.display_error(str(e))

    def display_response(self, response):
        response_text = self.builder.get_object('response_text')
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, f"Status Code: {response.status_code}\n\n")
        try:
            response_text.insert(tk.END, json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            response_text.insert(tk.END, response.text)

    def display_error(self, error_message):
        response_text = self.builder.get_object('response_text')
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, f"Error: {error_message}")

if __name__ == "__main__":
    app = AppUI()
    app.run()
