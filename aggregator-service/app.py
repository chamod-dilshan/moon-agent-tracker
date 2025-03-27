from flask import Flask, jsonify
from collections import defaultdict
import psycopg2
import os

app = Flask(__name__)

# 🔌 Redshift environment variables
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
REDSHIFT_DB = os.getenv('REDSHIFT_DB')
REDSHIFT_USER = os.getenv('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')
REDSHIFT_PORT = 5439

def get_redshift_connection():
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )

@app.route('/aggregate', methods=['GET'])
def aggregate():
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("SELECT agent_id, product_code, sale_amount FROM sales")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        totals_by_agent = defaultdict(float)
        totals_by_product = defaultdict(float)

        for row in rows:
            agent_id = row[0]
            product = row[1]
            amount = float(row[2])
            totals_by_agent[agent_id] += amount
            totals_by_product[product] += amount

        return jsonify({
            "total_sales_by_agent": totals_by_agent,
            "total_sales_by_product": totals_by_product
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Aggregator Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
