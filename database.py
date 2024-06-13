from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Base

# Database setup
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

# Drop all tables
Base.metadata.drop_all(engine)

# Create tables
Base.metadata.create_all(engine)

print("Database recreated successfully.")
