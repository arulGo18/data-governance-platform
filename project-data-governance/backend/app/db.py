from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time
import os

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# retry connection
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("Connected to Database")
        conn.close()
        break
    except Exception as e:
        print("Tunggu Connect", e)
        time.sleep(2)


SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()