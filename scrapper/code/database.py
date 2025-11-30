# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
import logging

MAX_RETRIES = 10
TOTAL_TIMEOUT = 60
DELAY_BETWEEN_RETRIES = TOTAL_TIMEOUT / MAX_RETRIES

Base = ""

for attempt in range(1, MAX_RETRIES + 1):
    try:
        database_url = os.getenv(
            "database_url",
            "mysql+pymysql://wine_user:secure_password@localhost:3306/wine_cellar"
        )

        logging.info(f"##### database_url = {database_url} ######")
        
        # Synchronous engine & session (simple and compatible)
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:      # test if connected to db
            conn.execute(text("SELECT 1"))
        print(f"[database] Connected to DB on attempt {attempt}")

        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        db = session_local()
        
        Base = declarative_base()
        
        logging.info(f"##### Start database_url = {database_url} ######")
        break
    except Exception as e:
        # print(e)
        logging.warning(f"Error connection DB: {attempt} {e} - Retrying in {DELAY_BETWEEN_RETRIES} seconds...")
        print(e)
        time.sleep(DELAY_BETWEEN_RETRIES)


def init_db():
    """
    Import models where Base metadata is declared and create tables.
    Called at startup.
    """
    Base.metadata.create_all(bind=engine) # type: ignore

init_db()