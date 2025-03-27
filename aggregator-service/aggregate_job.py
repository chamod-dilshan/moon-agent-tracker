from collections import defaultdict
from datetime import datetime
import psycopg2
import os

# 🔌 Redshift config
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

def aggregate_sales():
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

        print(f"[{datetime.now()}] Aggregated sales report:")
        print("Total Sales by Agent:")
        for agent, total in totals_by_agent.items():
            print(f"  - {agent}: ${total:.2f}")

        print("Total Sales by Product:")
        for product, total in totals_by_product.items():
            print(f"  - {product}: ${total:.2f}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    aggregate_sales()
