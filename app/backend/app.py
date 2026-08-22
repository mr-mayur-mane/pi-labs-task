from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "taskdb")
DB_USER = os.getenv("DB_USER", "app_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.route("/api")
def api_home():
    return jsonify({
        "message": "Task API is running"
    })


@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM tasks ORDER BY id")

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify([
        {
            "id": task[0],
            "name": task[1]
        }
        for task in tasks
    ])


@app.route("/api/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    task_name = data.get("name")

    if not task_name:
        return jsonify({
            "error": "Task name is required"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (name) VALUES (%s) RETURNING id",
        (task_name,)
    )

    task_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "id": task_id,
        "name": task_name
    }), 201


if __name__ == "__main__":

    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000
    )