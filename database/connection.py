from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

file_path = Path("main.db")

if not file_path.exists():
    with open(file_path, 'w') as file:
        file.write("")

engine = create_engine("sqlite:///main.db", echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    import database.models
    Base.metadata.create_all(bind=engine)
