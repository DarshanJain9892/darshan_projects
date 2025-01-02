from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

CONFIG_FILE = "config.properties"

# Function to read the configuration file
def read_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

# Function to write the configuration file
def write_config(config):
    with open(CONFIG_FILE, 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")

# Route to serve the HTML UI
@app.route('/')
def serve_ui():
    return send_from_directory('.', 'config_ui.html')  # Assumes the UI file is named `config_ui.html` and in the same folder

# Route to handle config updates
@app.route('/update-config', methods=['POST'])
def update_config():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    # Validate required keys
    expected_keys = {"api_url", "tps", "duration_in_seconds", "thread_count", "enable_screen"}
    if not expected_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required keys"}), 400

    # Update the config
    config = read_config()
    for key in expected_keys:
        config[key] = str(data[key])  # Ensure all values are strings for the properties file
    write_config(config)
    
    return jsonify({"message": "Configuration updated successfully!"})

# Start the server
if __name__ == '__main__':
    # Create a default configuration file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "api_url": "http://example.com",
            "tps": "50",
            "duration_in_seconds": "60",
            "thread_count": "10",
            "enable_screen": "true",
        }
        write_config(default_config)
    
    app.run(host='0.0.0.0', port=5000)
