import sqlalchemy as db
from dotenv import load_dotenv
import os
from hashlib import sha256

# load .env
load_dotenv()

TEMP_FOLDER = os.environ['TEMP_FOLDER']
DB_NAME = os.environ['DB_NAME']
DB_DATA = os.environ['DB_DATA']
DB_URI = f'sqlite:///{DB_NAME}'
DB_DATA_URI = f'sqlite:///{DB_DATA}'

ADMIN_USERNAME = os.environ['ADMIN_USERNAME']
ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
ADMIN_PASSWORD_HASH = sha256(ADMIN_PASSWORD.encode()).hexdigest()
SHARE_KEY_SEED = os.environ['SHARE_KEY_SEED']
API_KEY = os.environ['API_KEY']


if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

if os.path.exists(DB_DATA):
    os.remove(DB_DATA)

if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

engine = db.create_engine(DB_URI)
data_engine = db.create_engine(DB_DATA_URI)

# crete table for keep track of the image data
data_engine.execute("""
    CREATE TABLE 'counter' (
        id INTEGER NOT NULL,
        counter INTEGER,
        PRIMARY KEY (id)
    );
""")

data_engine.execute("""
    CREATE TABLE 'dataset' (
        id INTEGER NOT NULL,
        filename VARCHAR(32),
        tanggal VARCHAR(20),
        label VARCHAR(10),
        PRIMARY KEY (id)
    );
""")

data_engine.execute("""
    INSERT INTO 'counter'
    (counter)
    VALUES ('0')
""")

# create table for database
engine.execute("""
    CREATE TABLE 'users' (
        id INTEGER NOT NULL,
        username VARCHAR(32),
        password VARCHAR(64),
        PRIMARY KEY (id)
    );
""")

engine.execute("""
    CREATE TABLE 'share_keys' (
        id INTEGER NOT NULL,
        username VARCHAR(32),
        share_key VARCHAR(36),
        PRIMARY KEY (id)
    );
""")

engine.execute("""
    CREATE TABLE 'api_keys' (
        id INTEGER NOT NULL,
        api_key VARCHAR(36),
        PRIMARY KEY (id)
    );
""")

# insert data to database
engine.execute(f"""
    INSERT INTO 'users'
    (username, password)
    VALUES ('{ADMIN_USERNAME}', '{ADMIN_PASSWORD_HASH}')
""")

engine.execute(f"""
    INSERT INTO 'share_keys'
    (username, share_key)
    VALUES ('{ADMIN_USERNAME}', '{SHARE_KEY_SEED}')
""")

engine.execute(f"""
    INSERT INTO 'api_keys'
    (api_key)
    VALUES ('{API_KEY}')
""")

