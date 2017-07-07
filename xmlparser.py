import requests
import xml.sax
import os.path

class ExcelHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.chars = []
        self.cells = []
        self.rows = []
        self.tables = []

    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, atts):
        if name == "Cell":
            self.chars = []
        elif name == "Row":
            self.cells = []
        elif name == "Table":
            self.rows = []

    def endElement(self, name):
        if name == "Cell":
            self.cells.append(''.join(self.chars))
        elif name == "Row":
            self.rows.append(self.cells)
        elif name == "Table":
            self.tables.append(self.rows)

def getschedule(url):
    path = '.{}.xls'.format(url)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.isfile(path):
        # print("Downloading...")
        response = requests.get('http://www.sgu.ru{}/lesson'.format(url))
        # print("Done!")
        with open(path, 'wb') as output:
            output.write(response.content)


    excelHandler = ExcelHandler()
    xml.sax.parse(path, excelHandler)

    del excelHandler.rows[1][0]
    days = list([el, []] for el in (excelHandler.rows[1] + ['Воскресенье']))


    for i in range(len(days)):
        if i == 6:
            days[i][1].append('Воскресенье - занятий нет.\n\n')
            break
        for j in excelHandler.rows[2:]:
            if excelHandler.rows[2:].index(j) == 0:
                days[i][1].append('*08:20 – 9:50*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 1:
                days[i][1].append('*10:00 – 11:35*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 2:
                days[i][1].append('*12:05 – 13:40*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 3:
                days[i][1].append('*13:50 – 15:25*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 4:
                days[i][1].append('*15:35 – 17:10*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 5:
                days[i][1].append('*17:20 – 18:40*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 6:
                days[i][1].append('*18:45 – 20:10*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))
            elif excelHandler.rows[2:].index(j) == 7:
                days[i][1].append('*20:10 – 21:30*\n' + ('_- Занятий нет -_\n\n' if j[i + 1] == '' else j[i + 1]))

    days = list(''.join(day[1]) for day in days)

    days = [day.replace('\n\n ', '\n\n') for day in days]


    return days
