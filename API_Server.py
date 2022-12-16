from flask import Flask, request, render_template
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, db

from dotenv import load_dotenv
import os

import json

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# load enviroment variable from .env file
load_dotenv()

HOST_API = os.environ['HOST_API']
PORT_API = os.environ['PORT_API']
DB_NAME = os.environ["DB_NAME"]
DB_URI = f'sqlite:///{DB_NAME}'

Base = declarative_base()
engine = sql.create_engine(DB_URI)

cred = credentials.Certificate('./flooddetection-config.json')
app = firebase_admin.initialize_app(cred)
level = 0

ref = db.reference(url='https://flooddetection-e395c-default-rtdb.asia-southeast1.firebasedatabase.app/',
                    app=app)

app = Flask(__name__)
CORS(app, support_credentials=True)

color = ['green', 'blue', 'orange', 'red', 'black']
keadaan = ['Normal', 'Waspada', 'Siaga', 'Awas', 'Warning']

class APIKeys(Base):
    __tablename__ = 'api_keys'
    id = sql.Column(sql.Integer(), primary_key=True)
    api_key = sql.Column(sql.String(36))


@app.route("/")
def index():
    hostname = request.headers.get('Host')
    return render_template(
        'documentation.html',
        hostname = hostname
    ).encode(encoding='UTF-8')

@app.route('/api/status')
def status():
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    level = int(ref.child('level').get())
    api_key = request.args.get("api_key")
    API_KEY = dbSession.query(APIKeys).first()

    if api_key != API_KEY.api_key:
        return json.dumps({'message': 'API Keys Needed'})

    titik = {
        'x': [11660422.33186175],
        'y': [-331930.0131737783],
        'color': [color[level]],
        'keadaan': [keadaan[level]]
    }
    return json.dumps(titik)

if __name__ == "__main__":
    app.run(HOST_API, port=PORT_API, debug=True)
