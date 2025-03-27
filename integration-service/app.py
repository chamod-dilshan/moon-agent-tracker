from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import os
import uuid

app = Flask(__name__)

# Redshift connection settings (read from environment variables)
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

@app.route('/sales', methods=['POST'])
def record_sale():
    data = request.get_json()
    required_fields = ['agent_code', 'product', 'amount']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    sale_id = str(uuid.uuid4())
    sale_date = datetime.now().date()

    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sales (sale_id, agent_id, product_code, sale_amount, sale_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            sale_id,
            data['agent_code'],
            data['product'],
            float(data['amount']),
            sale_date
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[INFO] Sale added to Redshift: {sale_id}")
        return jsonify({"message": "Sale recorded to Redshift"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sales', methods=['GET'])
def get_sales():
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("SELECT sale_id, agent_id, product_code, sale_amount, sale_date FROM sales")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
