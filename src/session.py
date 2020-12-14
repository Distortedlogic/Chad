from decouple import config
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from src.schema import *

user = config("POSTGRES_USER")
password = config("POSTGRES_PASSWORD")
postgres_db = config("POSTGRES_DB")
DATABASE_URL = f"postgresql://{user}:{password}@127.0.0.1:5432/{postgres_db}"

db_engine = create_engine(DATABASE_URL, echo=False)
DBSession = sessionmaker(bind=db_engine)
db = DBSession()
