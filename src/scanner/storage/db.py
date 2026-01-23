from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scanner.storage.models import Base

DATABASE_URL = "postgresql+psycopg://scanner:scanner@localhost:5432/market_scanner"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    from scanner.storage.models import Base as CandleBase
    from scanner.storage.analysis_models import Base as AnalysisBase

    CandleBase.metadata.create_all(bind=engine)
    AnalysisBase.metadata.create_all(bind=engine)
