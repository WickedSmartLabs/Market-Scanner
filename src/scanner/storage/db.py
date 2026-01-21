from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scanner.storage.models import Base

DATABASE_URL = "postgresql+psycopg://scanner:scanner@localhost:5432/market_scanner"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
