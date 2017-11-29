from bs4 import BeautifulSoup
from urllib import request
import dbconn
import config

departments = {'bf': 'БИО',
                   'gf': 'ГЕОГР', 'gl': 'ГЕОЛ', 'ii': 'ИН.ИСК.', 'imo': 'ИИМО',
                   'ifk': 'ФКИС', 'ifg': 'ИФИЖ',  'ih': 'ИН.ХИМ.',
                   'mm': 'МЕХ-МАТ', 'sf': 'СОЦ',  'fi': 'ФИЯИЛ',
                   'knt': 'КНИИТ', 'fn': 'ФНИБТ',  'fnp': 'ФНП',
                   'fps': 'ПСИХ', 'fppso': 'ППИСО', 'ff': 'ФИЗФАК',
                   'fp': 'ФИЛОСОФ', 'ef': 'ЭКОНОМ', 'uf': 'ЮРФАК'
                   }

courses = {'1 курс':'1course', '2 курс':'2course',
           '3 курс':'3course', '4 курс':'4course',
           '5 курс':'5course', 'ДРУГОЕ':'OTHER'
           }

def get_session(url_group):
    url = "http://www.sgu.ru{}#session".format(url_group)
    f = request.urlopen(url)
    soup = BeautifulSoup(f.read(), 'html.parser')
    counter = 1
    text = ''
    try:
        for i in soup.find('table', id='session').find_all('tr'):
            if counter == 1:
                date, time, exam, subject = i.find_all('td')
                text += '<b>' + date.get_text()[:-1].strip() + '</b>, ' + \
                        time.get_text().strip() + '\n<i>' + exam.get_text().strip() + '</i>\n' + subject.get_text().strip() + '\n'
                counter += 1
            elif counter == 2:
                teacher, name = i.find_all('td')
                text += '<i>' + teacher.get_text()[:-1].strip() + '</i>\n' + name.get_text().strip() + '\n'
                counter += 1
            elif counter == 3:
                place, address = i.find_all('td')
                text += '<i>' + place.get_text()[:-1].strip() + '</i>\n' + address.get_text().strip() + '\n\n'
                counter = 1
        lastupdate = soup.find('div', attrs={'class': 'last-update'}).get_text()
        text = lastupdate.strip() + '\n\n' + text
    except:
        text = 'Расписания еще нет\n'
        lastupdate = soup.find('div', attrs={'class': 'last-update'}).get_text()
        text += lastupdate.strip() + '\n'
    print(text)
    return text

def get_groups(): # get all groups from parsed site

    db = dbconn.sqldb(config.database)

    db.delete_from_groups()

    completedata = []
    for department in departments.keys():
        print(departments[department])
        url = "http://www.sgu.ru/schedule/{}/".format(department)
        f = request.urlopen(url)
        soup = BeautifulSoup(f.read(), 'html.parser')
        for link in (soup.find_all('fieldset','do form_education form-wrapper')[0].find_all('fieldset','course form-wrapper')):
            for k in link.find_all('a'):
                course = link.legend.string[0:-1] if link.legend is not None else 'ДРУГОЕ'
                completedata.append( (k.get('href'), k.string, course,
                    courses[course],
                    departments[department], department)   )

    db.insert_into_groups(completedata)


if __name__ == '__main__':
    get_groups()