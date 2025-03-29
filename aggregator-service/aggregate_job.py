from collections import defaultdict
from datetime import datetime
import psycopg2
import mysql.connector
import os
import uuid
import requests

# 🌐 Notification service endpoint
NOTIFICATION_URL = os.getenv('NOTIFICATION_URL')

# 🔌 RDS MySQL Config
RDS_HOST = os.getenv('RDS_HOST')
RDS_DB = os.getenv('RDS_DB')
RDS_USER = os.getenv('RDS_USER')
RDS_PASSWORD = os.getenv('RDS_PASSWORD')
RDS_PORT = 3306

# 🔴 Redshift Config (for metrics)
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
REDSHIFT_DB = os.getenv('REDSHIFT_DB')
REDSHIFT_USER = os.getenv('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')
REDSHIFT_PORT = 5439

def get_rds_connection():
    return mysql.connector.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB
    )

def get_redshift_connection():
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )

def insert_metric_data(metric_type, entity_name, value):
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()

        # Mark previous metrics as inactive
        cur.execute("""
            UPDATE moonmetrics.sales_metrics
            SET is_latest = FALSE
            WHERE metric_type = %s AND entity_name = %s AND is_latest = TRUE
        """, (metric_type, entity_name))

        # Insert latest metric
        cur.execute("""
            INSERT INTO moonmetrics.sales_metrics (metric_id, metric_type, entity_name, value, is_latest)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (str(uuid.uuid4()), metric_type, entity_name, value))

        conn.commit()
        cur.close()
        conn.close()
        print(f"[METRIC] {metric_type} - {entity_name} = {value}")
    except Exception as e:
        print(f"[ERROR] Redshift insert failed: {e}")

def send_notification(agent_code, message):
    try:
        payload = {
            "agent_code": agent_code,
            "message": message
        }
        response = requests.post(NOTIFICATION_URL, json=payload)
        print(f"[NOTIFY] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Notification failed: {e}")

def aggregate_sales():
    try:
        # 🔄 Fetch raw data from RDS
        rds = get_rds_connection()
        cursor = rds.cursor()

        cursor.execute("SELECT agent_id, product_code, sale_amount FROM sales")
        sales_rows = cursor.fetchall()

        cursor.execute("SELECT agent_id, branch_name, team_name FROM agents")
        agent_rows = cursor.fetchall()

        cursor.execute("SELECT product_code, target_amount FROM product_targets")
        product_targets = {code: float(target) for code, target in cursor.fetchall()}

        cursor.close()
        rds.close()

        # Mapping agents
        agent_to_branch = {a: b for (a, b, _) in agent_rows}
        agent_to_team = {a: t for (a, _, t) in agent_rows}

        # Aggregation
        totals_by_agent = defaultdict(float)
        totals_by_product = defaultdict(float)
        totals_by_branch = defaultdict(float)
        totals_by_team = defaultdict(float)

        for agent_id, product, amount in sales_rows:
            amount = float(amount)
            totals_by_agent[agent_id] += amount
            totals_by_product[product] += amount

            branch = agent_to_branch.get(agent_id, "Unknown")
            team = agent_to_team.get(agent_id, "Unknown")
            totals_by_branch[branch] += amount
            totals_by_team[team] += amount

        print(f"[{datetime.now()}] Aggregating sales...")

        # ⬇️ Push to Redshift
        for agent, total in totals_by_agent.items():
            insert_metric_data("sales_by_agent", agent, total)

        for product, total in totals_by_product.items():
            insert_metric_data("sales_by_product", product, total)

            target = product_targets.get(product)
            if target and total >= target:
                insert_metric_data("product_achieved_target", product, total)
                send_notification("system", f"🎯 Sales target achieved for {product}! Total: ${total:.2f}, Target: ${target:.2f}")

        for branch, total in totals_by_branch.items():
            insert_metric_data("sales_by_branch", branch, total)

        for team, total in totals_by_team.items():
            insert_metric_data("sales_by_team", team, total)

        print("✅ Aggregation complete.")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

if __name__ == '__main__':
    aggregate_sales()
