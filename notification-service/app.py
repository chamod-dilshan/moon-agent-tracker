from flask import Flask, request, jsonify
import mysql.connector
import os
from datetime import datetime
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

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    
    if 'agent_code' not in data or 'message' not in data:
        return jsonify({"error": "Missing agent_code or message"}), 400

    notification_id = str(uuid.uuid4())

    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (notification_id, agent_id, message, sent_at)
            VALUES (%s, %s, %s, %s)
        """, (
            notification_id,
            data['agent_code'],
            data['message'],
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()

        print(f"[NOTIFICATION] ID: {notification_id} | Agent {data['agent_code']}: {data['message']}")
        return jsonify({"message": "Notification sent and logged", "notification_id": notification_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    try:
        conn = get_rds_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT notification_id, agent_id, message, sent_at
            FROM notifications
            ORDER BY sent_at DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        notifications = [
            {
                "notification_id": row[0],
                "agent_id": row[1],
                "message": row[2],
                "sent_at": row[3].isoformat()
            }
            for row in rows
        ]
        return jsonify(notifications), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Notification Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
