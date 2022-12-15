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



if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

engine = db.create_engine(DB_URI)
engine.execute("""
    CREATE TABLE 'users' (
        id INTEGER NOT NULL,
        username VARCHAR(32),
        password VARCHAR(64),
        PRIMARY KEY (id)
    );
""")

engine.execute(f"""
    INSERT INTO 'users'
    (username, password)
    VALUES ('{ADMIN_USERNAME}', '{ADMIN_PASSWORD_HASH}')
""")