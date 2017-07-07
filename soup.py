from bs4 import BeautifulSoup
from urllib import request
import dbconn
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

def get_groups(): # get all groups from parsed site

    db = dbconn.sqldb('departments.db')

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