from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

# Vérifier que DATABASE_URL existe
if not DATABASE_URL:
    raise RuntimeError(" ERROR: DATABASE_URL is missing from the .env file")


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
