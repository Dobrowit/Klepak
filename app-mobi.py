from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Folder, w którym będą zapisywane przesłane zdjęcia
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        gps_data = request.form.get('gps', '')
        return jsonify({'message': 'File uploaded successfully', 'gps': gps_data}), 200

if __name__ == '__main__':
    app.run(debug=True, port=20162)
