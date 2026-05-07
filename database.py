import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Only auto-create for server databases (e.g. Postgres). SQLite files are created implicitly.
    if DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
        if not database_exists(DATABASE_URL):
            create_database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(bind=engine)
