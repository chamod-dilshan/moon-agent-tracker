from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory sales store
sales = []

@app.route('/sales', methods=['POST'])
def record_sale():
    data = request.get_json()
    required_fields = ['agent_code', 'product', 'amount']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    sale_record = {
        "agent_code": data["agent_code"],
        "product": data["product"],
        "amount": float(data["amount"]),
        "timestamp": datetime.now().isoformat()
    }

    sales.append(sale_record)
    print(f"[INFO] New sale recorded: {sale_record}")
    return jsonify({"message": "Sale recorded"}), 201

@app.route('/sales', methods=['GET'])
def get_sales():
    return jsonify(sales)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
