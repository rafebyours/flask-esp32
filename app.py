import random  # For generating random sensor values
import time
from datetime import datetime
from flask import Flask, jsonify, request  # Tambahkan request di sini
from flask_cors import CORS  # Import CORS
from pymongo import MongoClient
import traceback  # Tambahkan traceback di sini

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['sensor_db']  # Use your database
collection = db['sensor_data']  # Use your collection

# Endpoint to get data
@app.route('/data', methods=['GET'])
def get_data():
    data = list(collection.find())
    for item in data:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        if 'timestamp' in item and isinstance(item['timestamp'], datetime):
            # Convert datetime to ISO 8601 format
            item['timestamp'] = item['timestamp'].isoformat() + "Z"
    return jsonify(data)

# Endpoint untuk menerima data dari ESP32
@app.route('/data', methods=['POST'])
def add_data():
    try:
        data = request.get_json()
        print("Data yang diterima:", data)  # Menampilkan data yang diterima

        required_keys = ['sensor_value_gas', 'sensor_value_humidity', 'sensor_value_temp']
        if not data or not all(key in data for key in required_keys):
            return jsonify({"error": f"Data tidak lengkap, harus mengandung {required_keys}"}), 400

        data['timestamp'] = datetime.utcnow().isoformat() + "Z"

        # Simpan ke MongoDB
        result = collection.insert_one(data)
        print(f"Data berhasil disimpan dengan ID: {result.inserted_id}")

        return jsonify({"message": "Data berhasil disimpan", "id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")  # Untuk melihat error yang lebih mendetail
        return jsonify({"error": "Terjadi kesalahan pada server"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run the Flask app
