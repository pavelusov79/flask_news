import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()

engine = create_engine(f'postgresql://{os.environ["DATABASE_USER"]}:{os.environ["DATABASE_PASSWORD"]}@localhost/flask_app')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    #import here all models
    from .models import User, Tags, Comments, News, Statistics
    Base.metadata.create_all(bind=engine)
