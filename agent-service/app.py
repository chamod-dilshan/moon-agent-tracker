from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory store for simplicity
agents = []

@app.route('/agents', methods=['GET'])
def get_agents():
    return jsonify(agents)

@app.route('/agents', methods=['POST'])
def add_agent():
    data = request.get_json()
    if 'id' not in data or 'name' not in data:
        return jsonify({"error": "Missing id or name"}), 400
    agents.append(data)
    return jsonify({"message": "Agent added successfully!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
