import sqlite3

def createtables():
    connection = sqlite3.connect('departments.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (url TEXT PRIMARY KEY, group_rus TEXT, course_rus TEXT, course_eng TEXT, dep_rus TEXT, dep_eng TEXT);
    ''')
    connection.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, dep_eng TEXT, group_id INTEGER, monday TEXT,
         tuesday TEXT, wednesday TEXT, thursday TEXT, friday TEXT, saturday TEXT, sunday TEXT, url TEXT);
    ''')
    connection.commit()