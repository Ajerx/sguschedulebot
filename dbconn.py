import sqlite3
import xmlparser

class sqldb:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_url_groups_by_department_and_course(self, department, course):
        with self.connection:
            self.cursor.execute('SELECT url, group_rus FROM groups WHERE dep_eng = ? AND course_eng = ?;', (department, course))
            data = self.cursor.fetchall()
            return data

    def select_course_by_department(self, department):
        with self.connection:
            self.cursor.execute('SELECT DISTINCT course_rus, course_eng FROM groups WHERE dep_eng = ?;', (department,))
            data = self.cursor.fetchall()
            return data

    def select_by_url(self, url):
        with self.connection:
            self.cursor.execute('SELECT dep_rus, group_rus, dep_eng FROM groups WHERE url = ?;', (url,))
            data = self.cursor.fetchone()
            return data

    def select_url_from_groups(self):
        with self.connection:
            self.cursor.execute('SELECT DISTINCT url FROM groups;')
            data = []
            for i in self.cursor.fetchall():
                data.append(i[0])
            return data

    def select_distinct_course(self):
        with self.connection:
            self.cursor.execute('SELECT DISTINCT course_eng FROM groups;')
            data = []
            for i in self.cursor.fetchall():
                data.append(i[0])
            return data

    def check_user(self, user_id):
        """ Проверяем, есть ли пользователь с таким id в базе """
        with self.connection:
            self.cursor.execute('SELECT * FROM users WHERE id = ?;', (user_id,))

            data = self.cursor.fetchone()
            if data is None:
                return False
            else:
                return True

    def insert_user_schedule(self, user_id, name, url):
        schedule_for_week = xmlparser.getschedule(url)

        department_and_group = self.select_by_url(url)[0:2]

        with self.connection:
            self.cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (user_id, name, *department_and_group, *schedule_for_week, url))
            self.connection.commit()

    def update_user_schedule(self, user_id, url):
        schedule_for_week = xmlparser.getschedule(url)

        department_and_group = self.select_by_url(url)[0:2]
        with self.connection:
            self.cursor.execute("UPDATE users SET dep_eng = ?, group_id = ?, monday = ?,"
                                "tuesday = ?, wednesday = ?,"
                                " thursday = ?, friday = ?, saturday = ?, sunday = ?, url = ? WHERE id = ?;",
                                (*department_and_group, *schedule_for_week, url, user_id))
            self.connection.commit()

    def get_schedule(self, user_id, dayweek):
        dayweeks = {0:'monday', 1:'tuesday', 2:'wednesday', 3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'}
        with self.connection:
            self.cursor.execute("SELECT {} FROM users WHERE id = ?;".format(dayweeks[dayweek]), (user_id,))
            schedule = self.cursor.fetchall()
            return schedule

    def update_schedule_by_url(self, url):
        schedule_for_week = xmlparser.getschedule(url)
        with self.connection:
            self.cursor.execute("UPDATE users SET monday = ?,"
                                "tuesday = ?, wednesday = ?,"
                                " thursday = ?, friday = ?, saturday = ?, sunday = ? WHERE url = ?;",
                                (*schedule_for_week, url))
            self.connection.commit()


    def get_urls_from_users(self):
        with self.connection:
            self.cursor.execute("SELECT url FROM users;")
            urls = []
            for i in self.cursor.fetchall():
                urls.append(i[0])
            return urls


    def delete_from_groups(self):
        with self.connection:
            self.cursor.execute("DELETE FROM groups;")
            self.connection.commit()

    def insert_into_groups(self, completedata):
        with self.connection:
            self.cursor.executemany('''

            INSERT INTO groups (url, group_rus, course_rus, course_eng, dep_rus, dep_eng) VALUES
            (?, ?, ?, ?, ?, ?)
            ''', completedata)

            self.connection.commit()

    def close(self):
        self.connection.close()