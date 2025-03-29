from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector
import os
import uuid

app = Flask(__name__)

# 🔌 RDS MySQL connection details
RDS_HOST = os.getenv('RDS_HOST')
RDS_DB = os.getenv('RDS_DB')
RDS_USER = os.getenv('RDS_USER')
RDS_PASSWORD = os.getenv('RDS_PASSWORD')
RDS_PORT = 3306

def get_rds_connection():
    return mysql.connector.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB
    )

@app.route('/sales', methods=['POST'])
def record_sale():
    data = request.get_json()
    required_fields = ['agent_code', 'product', 'amount']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    sale_id = str(uuid.uuid4())
    sale_date = datetime.now().date()

    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sales (sale_id, agent_id, product_code, sale_amount, sale_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            sale_id,
            data['agent_code'],
            data['product'],
            float(data['amount']),
            sale_date,
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()

        print(f"[INFO] Sale added to RDS: {sale_id}")
        return jsonify({"message": "Sale recorded to RDS", "sale_id": sale_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sales', methods=['GET'])
def get_sales():
    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sale_id, agent_id, product_code, sale_amount, sale_date
            FROM sales
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        sales = []
        for row in rows:
            sales.append({
                "sale_id": row[0],
                "agent_code": row[1],
                "product": row[2],
                "amount": float(row[3]),
                "sale_date": row[4].isoformat()
            })

        return jsonify(sales)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Integration Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
