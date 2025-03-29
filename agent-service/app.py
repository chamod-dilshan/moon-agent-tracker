from flask import Flask, request, jsonify
import mysql.connector
import os
from datetime import datetime

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

@app.route('/agents', methods=['POST'])
def add_agent():
    data = request.get_json()
    required_fields = ['id', 'name', 'email', 'branch', 'team', 'allowed_products']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO agents (agent_id, agent_name, email, branch_name, team_name, allowed_products, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['id'],
            data['name'],
            data['email'],
            data['branch'],
            data['team'],
            data['allowed_products'],
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Agent added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agents', methods=['GET'])
def get_agents():
    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT agent_id, agent_name, email, branch_name, team_name, allowed_products, created_at
            FROM agents
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

@app.route('/', methods=['GET'])
def home():
    return "Agent Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
