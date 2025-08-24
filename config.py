import os

class Config:
    # Secret key for Flask sessions and CSRF protection
    # IMPORTANT: In a production environment, this should be a strong, randomly generated string
    # and ideally loaded from an environment variable or a secure secret management system.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-secret-key-for-development'

    # Database configuration
    # This environment variable will determine which database is used.
    # Examples:
    # 1. SQLite (monolith): SQLALCHEMY_DATABASE_URI='sqlite:///site.db'
    # 2. PostgreSQL: SQLALCHEMY_DATABASE_URI='postgresql://user:password@host:port/database_name'
    # 3. Azure Cosmos DB (PostgreSQL API): SQLALCHEMY_DATABASE_URI='postgresql://user:password@host:port/database_name'
    #    (Note: The connection string for Cosmos DB's PostgreSQL API will look like a standard PostgreSQL string)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    
    # Disable SQLAlchemy event system to save memory, as we don't need it for this simple app
    SQLALCHEMY_TRACK_MODIFICATIONS = False

   ##
