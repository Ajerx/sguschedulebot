from apscheduler.schedulers.background import BackgroundScheduler
import os
import requests
import dbconn
import soup
import config


def sched():
    schedule = BackgroundScheduler()
    @schedule.scheduled_job('cron', hour=4)
    def scheduled_job():
        # update groups table
        soup.get_groups()

        # update xls files
        for root, directories, filenames in os.walk('./schedule/'):
            for filename in filenames:
                u = os.path.join(root, filename).replace("\\","/")

                response = requests.get('http://www.sgu.ru{}/lesson'.format(u[1:-4]))

                with open('{}'.format(u), mode='rb') as xlsfile:
                    fileContent = xlsfile.read()

                if fileContent != response.content:
                    with open('{}'.format(u), mode='wb') as f:
                        f.write(response.content)

        # update users table
        db = dbconn.sqldb(config.database)

        users_urls = db.get_urls_from_users()
        group_urls = db.select_url_from_groups()

        for url in users_urls:
            if url in group_urls:
                db.update_schedule_by_url(url)

    try:
        schedule.start()
    except (KeyboardInterrupt, SystemExit):
        pass