from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    
    if 'agent_code' not in data or 'message' not in data:
        return jsonify({"error": "Missing agent_code or message"}), 400
    
    # Simulate sending notification
    print(f"[NOTIFICATION] Agent {data['agent_code']}: {data['message']}")
    
    return jsonify({"message": "Notification sent"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Notification Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
