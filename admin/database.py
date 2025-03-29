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
SessionLocal = scoped_session(SessionFactory)

# Declared to create the base class for models
Base = declarative_base()

# Definition to get sessions
def get_session():
    session = SessionLocal
    try:
        yield session
    finally:
        session.close()