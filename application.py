from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
# --- MODIFIED FOR GCP ---
# We no longer need python-dotenv, App Engine will provide environment variables.
from google.cloud import secretmanager

app = Flask(__name__)

# --- ADDED FOR GCP: Securely fetch credentials ---
project_id = os.environ.get("GCP_PROJECT")
db_password_secret_name = os.environ.get("DB_SECRET_NAME")

def get_db_password():
    """Fetches the database password from Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{db_password_secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        # In a real app, you'd have more robust error handling and logging
        print(f"Error fetching secret: {e}")
        return None

# --- MODIFIED FOR GCP: Database configuration from Environment Variables ---
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': get_db_password(), # Fetch the password securely
    'host': os.getenv('DB_HOST'),   # This will be the Private IP of your Cloud SQL instance
    'database': os.getenv('DB_NAME'),
}

def get_db_connection():
    """Establishes a connection to the database."""
    # The password check is now implicitly handled by get_db_password() returning None on failure
    if not all(DB_CONFIG.values()):
         raise ConnectionError("Database configuration is incomplete. Check environment variables.")
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def init_db():
    """Initializes the database and creates the 'jobs' table if it doesn't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                location VARCHAR(255),
                job_type VARCHAR(50),
                posted_date DATE,
                job_description TEXT,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")

# Your routes (@app.route(...)) remain exactly the same.
# I have omitted them here for brevity, but you should keep them in your file.
# ... (Keep all your existing @app.route functions here) ...
# Make sure to call init_db() before the app runs

if __name__ == '__main__':
    # The init_db call can be placed here for local development
    # In a production App Engine environment, it will be called once on startup.
    init_db()
    app.run(debug=True)
else:
    # This is what Gunicorn will run.
    # Initialize the database when the application starts in production.
    init_db()
