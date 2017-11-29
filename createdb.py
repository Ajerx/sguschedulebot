import psycopg2
import config
import urllib.parse as urlparse

def createtables():

    url = urlparse.urlparse(config.database)

    connection = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (url TEXT PRIMARY KEY, group_rus TEXT, course_rus TEXT, course_eng TEXT, dep_rus TEXT, dep_eng TEXT);
    ''')
    connection.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, dep_eng TEXT, group_id TEXT, monday TEXT,
         tuesday TEXT, wednesday TEXT, thursday TEXT, friday TEXT, saturday TEXT, sunday TEXT, url TEXT, session TEXT);
    ''')
    connection.commit()
    connection.close()