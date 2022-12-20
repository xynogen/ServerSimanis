from flask import Flask, request, render_template, send_file
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, db, storage

from dotenv import load_dotenv
import os

import json
import io

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# load enviroment variable from .env file
load_dotenv()

HOST_API = os.environ['HOST_API']
PORT_API = os.environ['PORT_API']

DB_NAME = os.environ["DB_NAME"]
DB_URI = f'sqlite:///{DB_NAME}'

DEBUG = os.environ['DEBUG']

FIREBASE_CRED_FILE = os.environ['FIREBASE_CRED_FILE']
FIREBASE_BUCKET = os.environ['FIREBASE_BUCKET']
FIREBASE_URL = os.environ['FIREBASE_URL']

FILENAME = os.environ['FILENAME']
FILENAME_CLASS = os.environ['FILENAME_CLASS']

Base = declarative_base()
engine = sql.create_engine(DB_URI)

cred = credentials.Certificate(FIREBASE_CRED_FILE)
firebase_app = firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_BUCKET})
level = 0

ref = db.reference(url=FIREBASE_URL, app=firebase_app)

app = Flask(__name__)
CORS(app, support_credentials=True)

color = ['green', 'blue', 'orange', 'red', 'black']
keadaan = ['Normal', 'Waspada', 'Siaga', 'Awas', 'Warning']

class APIKeys(Base):
    __tablename__ = 'api_keys'
    id = sql.Column(sql.Integer(), primary_key=True)
    api_key = sql.Column(sql.String(36))


@app.route('/', methods=['GET'])
def index():
    hostname = request.headers.get('Host')
    return render_template(
        'documentation.html',
        hostname = hostname
    ).encode(encoding='UTF-8')

@app.route('/api/status', methods=['GET'])
def status():
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    api_key = request.args.get("api_key")
    API_KEY = dbSession.query(APIKeys).first()

    dbSession.close()

    if api_key != API_KEY.api_key:
        return json.dumps({'message': 'API Keys Needed'})

    level = int(ref.child('level').get())
    
    titik = {
        'x': [11660422.33186175],
        'y': [-331930.0131737783],
        'color': [color[level]],
        'keadaan': [keadaan[level]]
    }
    return json.dumps(titik)

@app.route('/api/capture', methods=['GET'])
def capture():
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    api_key = request.args.get("api_key")
    API_KEY = dbSession.query(APIKeys).first()
    
    dbSession.close()

    if api_key != API_KEY.api_key:
        return json.dumps({'message': 'API Keys Needed'})    

    bucket = storage.bucket(app=firebase_app)
    blob = bucket.get_blob(FILENAME_CLASS)
    image = blob.download_as_bytes()

    return send_file(
        io.BytesIO(image),
        mimetype='image/jpeg',
        as_attachment=False,
        download_name=f'{FILENAME}.jpg'
    )

@app.route('/api/download', methods=['GET'])
def download():
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    api_key = request.args.get("api_key")
    API_KEY = dbSession.query(APIKeys).first()
    
    dbSession.close()

    if api_key != API_KEY.api_key:
        return json.dumps({'message': 'API Keys Needed'})

    bucket = storage.bucket(app=firebase_app)
    blob = bucket.get_blob(FILENAME_CLASS)
    image = blob.download_as_bytes()

    return send_file(
        io.BytesIO(image),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=f'{FILENAME}.jpg'
    )

if __name__ == "__main__":
    debug = True if DEBUG == 'true' else False

    app.run('0.0.0.0', port=PORT_API, debug=debug)
