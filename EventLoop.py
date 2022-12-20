import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

import firebase_admin
from firebase_admin import credentials, db, storage

import requests
import numpy as np
import cv2

import datetime
import time

from ImageProcessor import Drawer, Points


load_dotenv()

FIREBASE_CRED_FILE = os.environ['FIREBASE_CRED_FILE']
FIREBASE_BUCKET = os.environ['FIREBASE_BUCKET']
FIREBASE_URL = os.environ['FIREBASE_URL']

API_KEY = os.environ['API_KEY']
HOST_API = os.environ['HOST_API']

PORT_API = os.environ['PORT_API']
DB_DATA = os.environ['DB_DATA']

DB_URI = f'sqlite:///{DB_DATA}'
URL = f'http://{HOST_API}:{PORT_API}/api/capre?api_key={API_KEY}'

FILENAME = os.environ['FILENAME']
FILENAME_CLASS = os.environ['FILENAME_CLASS']

TEMP_FOLDER = os.environ['TEMP_FOLDER']

DEBUG = os.environ['DEBUG']
INTERVAL = os.environ['INTERVAL']
INTERVAL = int(INTERVAL)

cred = credentials.Certificate(FIREBASE_CRED_FILE)
firebase_app = firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_BUCKET})
ref = db.reference(url=FIREBASE_URL, app=firebase_app)
Base = declarative_base()
engine = sql.create_engine(DB_URI)
level = 0

class Counter(Base):
    __tablename__ = 'counter'
    id = sql.Column(sql.Integer(), primary_key=True)
    counter = sql.Column(sql.Integer())

class Dataset(Base):
    __tablename__ = 'dataset'
    id = sql.Column(sql.Integer(), primary_key=True)
    tanggal = sql.Column(sql.String(32))
    filename = sql.Column(sql.String(20))
    label = sql.Column(sql.String(10))

while True:
    response = requests.get(URL, stream=True).raw
    image = np.asarray(bytearray(response.read()), dtype='uint8')
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    img_H = image.shape[0]
    img_W = image.shape[1]
    pts = Points.Points(Point_A = [537, 574],
                            Point_B = [624, 568],
                            Point_C = [535, 519],
                            Point_D = [625, 516],
                            img_H = img_H,
                            img_W = img_W)

    # for testing
    if DEBUG == 'test':
        def get_mouse_position(event,x,y,flags,param):
            global mouseX,mouseY
            if event == cv2.EVENT_LBUTTONDBLCLK:
                mouseX,mouseY = x,y
                print(f'Mouse X : {mouseX}')
                print(f'Mouse Y : {mouseY}')

            
        cv2.imshow('image', image)
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', get_mouse_position)

        cv2.waitKey(0)
        cv2.destroyAllWindows()


    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    firebase_counter = ref.child('data_counter').get()
    firebase_counter = int(firebase_counter)
    db_counter = dbSession.query(Counter).filter(Counter.id == 1).first()
    db_counter = int(db_counter.counter)

    if db_counter < firebase_counter:
        dbSession.query(Counter).filter(Counter.id == 1).update({'counter': str(firebase_counter)})
        dbSession.commit()
        ref.child('data_counter').set(str(firebase_counter +1))
        
        drawer = Drawer.Drawer(image, pts)

        image_warped = drawer.get_warped_image()

        # predict the data with tensorflow image_warped
        level = 3
        ref.child('level').set(str(level))

        drawer.draw_line(level)
        drawer.draw_dot(level)

        image_class = drawer.get_image_canvas()

        date = datetime.datetime.now()
        tanggal = date.strftime('%Y-%m-%d')
        tanggal = str(tanggal)
        jam = date.strftime('%H-%M-%S')

        FILEFOLDER = f'{TEMP_FOLDER}/{tanggal}'
        FILEPATH = f'{FILEFOLDER}/{jam}.jpg'

        if not os.path.exists(FILEFOLDER):
            os.mkdir(FILEFOLDER)

        cv2.imwrite(FILEPATH, image_class)

        bucket = storage.bucket(app=firebase_app)
        blob = bucket.blob(FILENAME_CLASS)
        blob.upload_from_filename(FILEPATH)
        print("[INFO] Image Has Been Uploaded")

    dbSession.close()
    time.sleep(INTERVAL)







