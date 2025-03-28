from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# 🔌 Redshift connection details
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST', 'moonagent-cluster.cpcjx7hrgnyr.ap-southeast-2.redshift.amazonaws.com')
REDSHIFT_DB = os.getenv('REDSHIFT_DB', 'moonmetrics_db')
REDSHIFT_USER = os.getenv('REDSHIFT_USER', 'admin')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD', 'DATAst2012')
REDSHIFT_PORT = 5439

def get_redshift_connection():
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )

@app.route('/agents', methods=['POST'])
def add_agent():
    data = request.get_json()
    required_fields = ['id', 'name', 'email', 'branch', 'team', 'allowed_products']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO moontracker.agents (agent_id, agent_name, email, branch_name, team_name, allowed_products)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['id'],
            data['name'],
            data['email'],
            data['branch'],
            data['team'],
            data['allowed_products']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Agent added to Redshift successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agents', methods=['GET'])
def get_agents():
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT agent_id, agent_name, email, branch_name, team_name, allowed_products, created_at
            FROM moontracker.agents
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        agents = [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "branch": row[3],
                "team": row[4],
                "allowed_products": row[5],
                "created_at": str(row[6])
            } for row in rows
        ]
        return jsonify(agents)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
