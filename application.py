# app.py
from flask import Flask
from extensions import db, login_manager
from datetime import datetime, timezone
import os

# --- GCP ADAPTATION: Import Secret Manager client ---
from google.cloud import secretmanager

# --- GCP ADAPTATION: dotenv is no longer used in production ---
# load_dotenv() is removed.

# --- GCP ADAPTATION: Function to securely fetch the database password ---
def get_db_password():
    """Fetches the database password from Google Cloud Secret Manager."""
    try:
        # These environment variables will be set in app.yaml
        project_id = os.environ.get("GCP_PROJECT")
        secret_name = os.environ.get("DB_SECRET_NAME")

        if not project_id or not secret_name:
            print("GCP_PROJECT or DB_SECRET_NAME environment variables not set.")
            return None

        client = secretmanager.SecretManagerServiceClient()
        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        # Return the decoded secret payload
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        # In a real production app, you would log this error
        print(f"Error fetching secret from Secret Manager: {e}")
        return None

# Initialise Flask application
app = Flask(__name__)

# --- GCP ADAPTATION: Build the database URI and configure the app directly ---
# We no longer use the Config class from config.py for the database URI.

# 1. Fetch all the necessary components for the connection string
db_user = os.environ.get('DB_USER')
db_pass = get_db_password() # Securely fetched password
db_host = os.environ.get('DB_HOST') # The private IP of your Cloud SQL instance
db_name = os.environ.get('DB_NAME')

# 2. Set the application's secret key for session management
# This should be a long, random string. For production, this should also be in Secret Manager.
# For this project, setting it as an environment variable is sufficient.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-fallback-secret-key')

# 3. Construct the SQLAlchemy Database URI
# Format: mysql+mysqlconnector://<user>:<password>@<host>/<dbname>
if all([db_user, db_pass, db_host, db_name]):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}"
    )
else:
    print("Database connection details are missing. Check environment variables.")
    # You might want to handle this more gracefully, but for now, we'll print an error.
    app.config['SQLALCHEMY_DATABASE_URI'] = None

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise extensions with the Flask app
db.init_app(app)
login_manager.init_app(app)

# Configure Login Manager (this logic remains the same)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models and routes after initialising to avoid circular imports
# This structure remains the same
from models import User, Job
from routes import *

# This block ensures that database tables are created if they don't exist.
# This is excellent practice and should be kept.
with app.app_context():
    if app.config['SQLALCHEMY_DATABASE_URI']:
        db.create_all()
    else:
        print("Skipping db.create_all() because database URI is not configured.")

# This context processor remains the same
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

# This block is for local development and will not be used by Gunicorn in production
if __name__ == '__main__':
    # Note: For local testing, you would need to set the environment variables manually
    # or use a different method to load them.
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
