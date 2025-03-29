from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# 🔌 Redshift connection details
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

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    
    if 'agent_code' not in data or 'message' not in data:
        return jsonify({"error": "Missing agent_code or message"}), 400

    notification_id = str(uuid.uuid4())  # ✅ Generate unique notification ID
    
    # Log notification to Redshift
    try:
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO moontracker.notifications (notification_id, agent_id, message, sent_at)
            VALUES (%s, %s, %s, %s)
        """, (notification_id, data['agent_code'], data['message'], datetime.now()))
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
        conn = get_redshift_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT notification_id, agent_id, message, sent_at
            FROM moontracker.notifications
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
