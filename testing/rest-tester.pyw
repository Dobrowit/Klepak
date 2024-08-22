import requests
import json
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "gui.ui"
RESOURCE_PATHS = [PROJECT_PATH]

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
        
    def btn_get(self):
        url = self.builder.get_object('url_entry').get()
        try:
            response = requests.get(url)
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
            response_text.insert(tk.END, json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            response_text.insert(tk.END, response.text)

    def display_error(self, error_message):
        response_text = self.builder.get_object('response_text')
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, f"Error: {error_message}")

if __name__ == "__main__":
    app = AppUI()
    app.run()
