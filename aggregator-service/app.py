from flask import Flask, jsonify
from collections import defaultdict

app = Flask(__name__)

# Simulated sales data (in a real app, you'd pull from DB or another service)
sales = [
    {"agent_code": "A101", "product": "LifeCover-Plus", "amount": 1200.0},
    {"agent_code": "A102", "product": "Health-Protect", "amount": 900.0},
    {"agent_code": "A101", "product": "LifeCover-Plus", "amount": 1000.0},
    {"agent_code": "A103", "product": "Health-Protect", "amount": 600.0},
    {"agent_code": "A102", "product": "LifeCover-Plus", "amount": 800.0}
]

@app.route('/aggregate', methods=['GET'])
def aggregate():
    totals_by_agent = defaultdict(float)
    totals_by_product = defaultdict(float)

    for sale in sales:
        totals_by_agent[sale["agent_code"]] += sale["amount"]
        totals_by_product[sale["product"]] += sale["amount"]

    return jsonify({
        "total_sales_by_agent": totals_by_agent,
        "total_sales_by_product": totals_by_product
    })

@app.route('/', methods=['GET'])
def home():
    return "Aggregator Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
