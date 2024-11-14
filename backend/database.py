from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
import os

dotenv.load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite://"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
