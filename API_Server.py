import json
from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate("./flooddetection-config.json")
app = firebase_admin.initialize_app(cred)
level = 0

ref = db.reference(url='https://flooddetection-e395c-default-rtdb.asia-southeast1.firebasedatabase.app/',
                    app=app)

app = Flask(__name__)
CORS(app, support_credentials=True)

color = ['green', 'blue', 'orange', 'red', 'black']
keadaan = ['Normal', 'Waspada', 'Siaga', 'Awas', 'Berbahaya']

@app.route('/api/status')
def circle():
    level = int(ref.child('level').get())
    titik = {
        'x': [11660422.33186175],
        'y': [-331930.0131737783],
        'color': [color[level]],
        'keadaan': [keadaan[level]]
    }
    return json.dumps(titik)

if __name__ == "__main__":
    app.run('0.0.0.0', port=8081, debug=True)
