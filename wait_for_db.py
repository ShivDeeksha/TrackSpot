import time
import psycopg2
from psycopg2 import OperationalError
import os

def wait_for_db():
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', 5432)

    while True:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.close()
            break
        except OperationalError:
            print("Database is not ready, waiting...")
            time.sleep(1)

if __name__ == '__main__':
    wait_for_db()
