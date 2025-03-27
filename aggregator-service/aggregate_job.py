from collections import defaultdict
from datetime import datetime
import psycopg2
import os
import uuid

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

def insert_metric_data(metric_type, entity_name, value):
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sales_metrics (metric_id, metric_type, entity_name, value)
            VALUES (%s, %s, %s, %s)
        """, (str(uuid.uuid4()), metric_type, entity_name, value))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[METRIC INSERTED] {metric_type} - {entity_name} = {value}")
    except Exception as e:
        print(f"[ERROR] Failed to insert metric: {e}")

def aggregate_sales():
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()

        # Get all sales
        cur.execute("SELECT agent_id, product_code, sale_amount FROM sales")
        sales_rows = cur.fetchall()

        # Get agent metadata (for branch and team mapping)
        cur.execute("SELECT agent_id, branch_name, team_name FROM agents")
        agent_meta_rows = cur.fetchall()
        cur.close()
        conn.close()

        # Mapping for agents to branch/team
        agent_to_branch = {}
        agent_to_team = {}

        for agent_id, branch, team in agent_meta_rows:
            agent_to_branch[agent_id] = branch
            agent_to_team[agent_id] = team

        # Aggregations
        totals_by_agent = defaultdict(float)
        totals_by_product = defaultdict(float)
        totals_by_branch = defaultdict(float)
        totals_by_team = defaultdict(float)

        for agent_id, product, amount in sales_rows:
            amount = float(amount)
            totals_by_agent[agent_id] += amount
            totals_by_product[product] += amount

            branch = agent_to_branch.get(agent_id, 'Unknown')
            team = agent_to_team.get(agent_id, 'Unknown')

            totals_by_branch[branch] += amount
            totals_by_team[team] += amount

        print(f"[{datetime.now()}] Aggregating and inserting sales metrics...")

        for agent, total in totals_by_agent.items():
            insert_metric_data('sales_by_agent', agent, total)

        for product, total in totals_by_product.items():
            insert_metric_data('sales_by_product', product, total)

        for branch, total in totals_by_branch.items():
            insert_metric_data('sales_by_branch', branch, total)

        for team, total in totals_by_team.items():
            insert_metric_data('sales_by_team', team, total)

        print("Aggregation complete!")

    except Exception as e:
        print(f"[ERROR] Aggregation failed: {e}")

if __name__ == '__main__':
    aggregate_sales()