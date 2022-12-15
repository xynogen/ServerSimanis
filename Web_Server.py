from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.tile_providers import OSM
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import AjaxDataSource, HoverTool, TapTool, OpenURL
import pandas as pd

from dotenv import load_dotenv
import os

from datetime import timedelta
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_cors import CORS

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from hashlib import sha256
import uuid

# load enviroment variable from .env file
load_dotenv()
HOST_API = os.environ['HOST_API']
PORT_API = os.environ['PORT_API']
HOST_WEB = os.environ['HOST_WEB']
PORT_WEB = os.environ['PORT_WEB']
DATA_URL = f'http://{HOST_API}:{PORT_API}/api/status'

DB_NAME = os.environ["DB_NAME"]
DB_URI = f'sqlite:///{DB_NAME}'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'waterlevel-webserver'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
CORS(app, support_credentials=True)

Base = declarative_base()
engine = db.create_engine(DB_URI)

class Users(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(64))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

color = ['green', 'blue', 'orange', 'red', 'black']
keadaan = ['Normal', 'Waspada', 'Siaga', 'Awas', 'Warning']
share_keys = {}

hoverRectangle = AjaxDataSource(
    data_url = DATA_URL,
    polling_interval = 1000,
    method = 'GET',
    mode = 'replace'
)

titik_kamera = ColumnDataSource(data=dict(
        x=[11660422.33186175],
        y=[-331930.0131737783]
    )
)

aliran_sungai = pd.read_csv('aliran_sungai.csv')
aliran_sungai['x'] = aliran_sungai['x'].apply(lambda x: list(x[1:-1].split(',')))
aliran_sungai['y'] = aliran_sungai['y'].apply(lambda x: list(x[1:-1].split(',')))
aliran_sungai = ColumnDataSource(aliran_sungai)

TOOLTIPS = [
    ('Keadaan', '@keadaan')
]

p = figure(width=1360, height=600)
p.sizing_mode = 'scale_width'
p.match_aspect = True
p.xgrid.visible = False
p.ygrid.visible = False
p.xaxis.major_tick_line_color = None
p.xaxis.minor_tick_line_color = None
p.yaxis.major_tick_line_color = None
p.yaxis.minor_tick_line_color = None
p.xaxis.major_label_text_font_size = '0pt'
p.yaxis.major_label_text_font_size = '0pt'

p.add_tile(OSM)
p.circle('x', 'y', color='green', source=titik_kamera, name='circle', size=5)
p.multi_line('x', 'y', source=aliran_sungai, line_color='green', line_width=1, name='line')

mockupHover = p.square('x', 'y', alpha = 0, source=hoverRectangle, size = 1100)
p.add_tools(HoverTool(renderers=[mockupHover], tooltips=TOOLTIPS, line_policy='interp', description = 'Hover Sungai'))
p.add_tools(TapTool(renderers=[mockupHover], callback=OpenURL(url='/cctv'), description = 'TapTool Sungai', name='taptool'))

p.legend.title = 'Level Ketinggian Air'
p.circle('x', 'y', source=titik_kamera, size=0, color=color[0], legend_label=keadaan[0])
p.circle('x', 'y', source=titik_kamera, size=0, color=color[1], legend_label=keadaan[1])
p.circle('x', 'y', source=titik_kamera, size=0, color=color[2], legend_label=keadaan[2])
p.circle('x', 'y', source=titik_kamera, size=0, color=color[3], legend_label=keadaan[3])
p.circle('x', 'y', source=titik_kamera, size=0, color=color[4], legend_label=keadaan[4])
p.line([11660422.33186175, 11660422.3319], [-331930.0131737783, -331930.0231737783], line_width=1, color='royalblue', legend_label='Garis DAS')

script, div = components(p)


@app.route('/login', methods=['GET'])
def login_get():
    loginForm = LoginForm()

    if 'username' in session:
        return redirect(url_for('map'))

    return render_template(
        'login.html',
        loginForm=loginForm
    ).encode(encoding='UTF-8')

@app.route('/login', methods=['POST'])
def login_post():
    loginForm = LoginForm()
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()
    _username = ''
    _password = ''

    if not loginForm.validate_on_submit():
        flash('Invalid Password or Username', 'error')
        return redirect(url_for('login_get'))

    _username = loginForm.username.data
    _password = loginForm.password.data
    _password_hash = sha256(_password.encode()).hexdigest()
    
    hasil = dbSession.query(Users).filter(Users.username == f"{_username}").all()

    if len(hasil) == 0:
        flash('Wrong Username', 'error')
        return redirect(url_for('login_get'))

    if len(hasil) > 1:
        flash('More than One User Found', 'error')
        return redirect(url_for('login_get'))
    
    if hasil[0].password != _password_hash:
        flash('Wrong Password', 'error')
        return redirect(url_for('login_get')) 

    session['username'] = _username
    share_keys[_username] = str(uuid.uuid4())
    return redirect(url_for('map'))


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' not in session:
        return redirect(url_for('login_get'))

    share_keys[session['username']] = []
    session.pop("username")
    return redirect(url_for("index"))

@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login_get'))
        
    return redirect(url_for('map'))

@app.route('/map', methods=['GET'])
def map():
    if 'username' not in session:
        return redirect(url_for('login_get'))
    
    try:
        SHARE_URL = f"http://{HOST_WEB}:{PORT_WEB}/share?view=map&key={share_keys[session['username']]}"
    except:
        share_keys[session['username']] = str(uuid.uuid4())
        SHARE_URL = f"http://{HOST_WEB}:{PORT_WEB}/share?view=map&key={share_keys[session['username']]}"
    

    return render_template(
        'map.html',
        plot_script = script,
        plot_div = div,
        js_resources = INLINE.render_js(),
        css_resources = INLINE.render_css(),
        DATA_URL = DATA_URL,
        SHARE_URL = SHARE_URL,
        username=session['username']
        ).encode(encoding='UTF-8')

@app.route('/share', methods=['GET'])
def share():
    view = request.args.get('view')
    share_key = request.args.get('key')

    if share_key not in share_keys.values():
        flash('Invalid Link, Please Relogin', 'error')
        return redirect(url_for('login_get'))

    if view == 'map':
        return render_template(
            'share_map.html',
            share_key = share_key,
            plot_script = script,
            plot_div = div,
            js_resources = INLINE.render_js(),
            css_resources = INLINE.render_css(),
        ).encode(encoding='UTF-8')
    elif view == 'cctv':
        return render_template(
            'share_cctv.html',
            share_key = share_key
        ).encode(encoding='UTF-8')
    else:
        flash('Invalid View, Please Check the Link Again', 'error')
        return redirect(url_for('login_get'))

@app.route('/cctv', methods=['GET'])
def cctv():
    if 'username' not in session:
        return redirect(url_for('login_get'))
    
    try:
        SHARE_URL = f"http://{HOST_WEB}:{PORT_WEB}/share?view=map&key={share_keys[session['username']]}"
    except:
        share_keys[session['username']] = str(uuid.uuid4())
        SHARE_URL = f"http://{HOST_WEB}:{PORT_WEB}/share?view=map&key={share_keys[session['username']]}"

    return render_template(
        'cctv.html',
        SHARE_URL=SHARE_URL,
        username=session['username']
    ).encode(encoding='UTF-8')

@app.route('/refresh', methods=['GET'])
def refresh():
    if 'username' not in session:
        return redirect(url_for('login_get'))
    
    share_keys[session['username']] = str(uuid.uuid4())
    return redirect(url_for('map'))


if __name__ == '__main__':
    app.run(HOST_WEB, port=PORT_WEB, debug=True)