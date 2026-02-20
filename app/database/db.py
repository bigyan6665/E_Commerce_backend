from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.app_config import getAppConfig

Base = declarative_base()

config = getAppConfig()

engine = create_engine(url = config.database_url)
SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)


# This pattern ensures each request gets its own session that is automatically cleaned up.
def get_db():
    db = SessionLocal() # creates a new connection to the db
    try:
        yield db
        # This makes get_db a Python generator. 
        # Donot use return db
    finally:
        db.close() # closes the connection