from api_request import mock_fetch
import psycopg2  
def connect_to_db():
    print('connecting to the postgresql database')

    try:
        conn=psycopg2.connect(
            host='localhost',
            port=5000,
            dbname='db',
            user='db_user',
            password='db_password'

        )
        print(conn)
    except psycopg2.Error as e:
        print('error occured')
        raise

def create_table(conn):
    print('creating table if not exist....')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS dev;
            CREATE TABlE IF NOT EXISTS dev.raw_weather_data (
                       id SERIAL PRIMARY KEY,
                       city TEXT,
                       temperature FLOAT,
                       weather_descriptions TEXT,
                       wind_speed FLOAT,
                       time TIMESTAMP,
                       inserted_at TIMESTAMP DEFAULT NOW(),
                       utc_offset TEXT
                       );

""")
        conn.commit()
        print('table was created...')
    except psycopg2.Error as e:
        print(f'ffailed to create table {e}')
        raise
conn=connect_to_db()
create_table(conn)