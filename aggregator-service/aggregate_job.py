from collections import defaultdict
from datetime import datetime
import psycopg2
import os
import uuid
import requests

# 🔌 Redshift config
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
REDSHIFT_DB = os.getenv('REDSHIFT_DB')
REDSHIFT_USER = os.getenv('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')
REDSHIFT_PORT = 5439

# 🔔 Notification service endpoint
NOTIFICATION_URL = os.getenv('NOTIFICATION_URL')

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

        # Mark previous metrics of the same type/entity as not latest
        cur.execute("""
            UPDATE moontracker.sales_metrics
            SET is_latest = FALSE
            WHERE metric_type = %s AND entity_name = %s AND is_latest = TRUE
        """, (metric_type, entity_name))

        # Insert new metric as latest
        cur.execute("""
            INSERT INTO moontracker.sales_metrics (metric_id, metric_type, entity_name, value, is_latest)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (str(uuid.uuid4()), metric_type, entity_name, value))

        conn.commit()
        cur.close()
        conn.close()
        print(f"[METRIC INSERTED] {metric_type} - {entity_name} = {value}")

    except Exception as e:
        print(f"[ERROR] Failed to insert metric: {e}")

def send_notification(agent_code, message):
    try:
        payload = {
            "agent_code": agent_code,
            "message": message
        }
        response = requests.post(NOTIFICATION_URL, json=payload)
        print(f"[NOTIFY] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to notify: {e}")

def aggregate_sales():
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()

        # Fetch sales data
        cur.execute("SELECT agent_id, product_code, sale_amount FROM moontracker.sales")
        sales_rows = cur.fetchall()

        # Fetch agent metadata
        cur.execute("SELECT agent_id, branch_name, team_name FROM moontracker.agents")
        agent_meta_rows = cur.fetchall()

        # Fetch product targets
        cur.execute("SELECT product_code, target_amount FROM moontracker.product_targets")
        product_target_rows = cur.fetchall()

        cur.close()
        conn.close()

        # Prepare mappings
        agent_to_branch = {aid: b for (aid, b, _) in agent_meta_rows}
        agent_to_team = {aid: t for (aid, _, t) in agent_meta_rows}
        product_targets = {p: float(t) for (p, t) in product_target_rows}

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

        print(f"[{datetime.now()}] Aggregating sales and pushing metrics...")

        # Insert metrics
        for agent, total in totals_by_agent.items():
            insert_metric_data("sales_by_agent", agent, total)

        for product, total in totals_by_product.items():
            insert_metric_data("sales_by_product", product, total)

            # Check for targets and notify if met
            target = product_targets.get(product)
            if target and total >= target:
                insert_metric_data('product_achieved_target', product, total)
                send_notification("system", f"Sales target achieved for {product}! Total: ${total:.2f}, Target: ${target:.2f}")

        for branch, total in totals_by_branch.items():
            insert_metric_data("sales_by_branch", branch, total)

        for team, total in totals_by_team.items():
            insert_metric_data("sales_by_team", team, total)

        print("Aggregation complete.")

    except Exception as e:
        print(f"[ERROR] Aggregation failed: {e}")

if __name__ == '__main__':
    aggregate_sales()
