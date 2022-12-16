import sqlalchemy as db
from dotenv import load_dotenv
import os
from hashlib import sha256

# load .env
load_dotenv()

DB_NAME = os.environ["DB_NAME"]
DB_URI = f'sqlite:///{DB_NAME}'

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
ADMIN_PASSWORD_HASH = sha256(ADMIN_PASSWORD.encode()).hexdigest()
SHARE_KEY = "41949048-66e8-46ca-88d3-0a14c93876ea"
API_KEY = "dca767e7-308d-4fcd-8f82-6c9766f3940b"



if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

engine = db.create_engine(DB_URI)

# create table
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
    VALUES ('{ADMIN_USERNAME}', '{SHARE_KEY}')
""")

engine.execute(f"""
    INSERT INTO 'api_keys'
    (api_key)
    VALUES ('{API_KEY}')
""")

