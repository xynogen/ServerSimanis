import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

DB_NAME = os.environ["DB_NAME"]
DB_URI = f'sqlite:///{DB_NAME}'

Base = declarative_base()
engine = db.create_engine(DB_URI)

class Users(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(64))


DBSession = sessionmaker(bind=engine)
dbSession = DBSession()

hasil = dbSession.query(Users).filter(Users.username == "admin").all()
for has in hasil:
    print(has.password)