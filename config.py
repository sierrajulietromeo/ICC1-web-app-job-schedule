# config.py
import os, urllib.parse

class Config:
    # sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-secret-key-for-development'

    # Prefer DATABASE_URL (for local/dev). If not set, try the KV-injected connection string.
    # Your KV ref is in app setting: ConnectionStrings__Default
    ADO = os.environ.get("ConnectionStrings__Default", "")
    if ADO:
        # Use SQL Server via pyodbc
        SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(ADO)}"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


   
