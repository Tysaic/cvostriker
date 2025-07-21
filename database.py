from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Config Database
DATABASE_URL = 'sqlite:///database.db'

# Create and Setting the engine
engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    future=True
)

# Create the session maker
SessionFactory = sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False, 
    future=True,
    expire_on_commit=True
)

# Each request need to create new session with scoped_session
Session = scoped_session(SessionFactory)

# Declared to create the base class for models
Base = declarative_base()

# Definition to get sessions
def get_session():
    session = Session
    try:
        yield session
    finally:
        session.close()


"""
#Forma robusta de configurar
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.name = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.driver = os.getenv('DB_DRIVER', 'postgresql')
    
    def get_database_url(self):
        if not all([self.name, self.user, self.password]):
            raise ValueError("Missing required database environment variables")
        
        # URL encode password to handle special characters
        encoded_password = quote_plus(self.password)
        
        return f"{self.driver}://{self.user}:{encoded_password}@{self.host}:{self.port}/{self.name}"

# Usage
try:
    db_config = DatabaseConfig()
    DATABASE_URL = db_config.get_database_url()
except ValueError as e:
    print(f"Database configuration error: {e}")
    DATABASE_URL = 'sqlite:///database.db'  # Fallback


"""