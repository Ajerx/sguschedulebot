# -*- coding: utf-8 -*-
from datetime import date, timedelta
import config
import telebot
from telebot import types
import updatebyschedule
import dbconn
import os
import soup
import botan
import createdb
import time
import sys


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('📚 Узнать расписание')
    markup.row('📝 Сменить группу')
    bot.send_message(message.chat.id, 'Привет. '
    'Это бот, который поможет узнать свое расписание. Он создан для студентов дневного отделения Саратовского Государственного Университета.'
                                      ' Введите /help для получения информации о боте.'
    , reply_markup=markup)
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    y =[]
    for key, value in soup.departments.items():
        y.append(types.InlineKeyboardButton(text="{}".format(value), callback_data="{}".format(key)))

    keyboard.add(*y)
    bot.send_message(message.chat.id, "Выберите свой факультет:", reply_markup=keyboard)
    botan.track(config.botan_key, message.chat.id, message, '/start')

@bot.message_handler(regexp='^📚 Узнать расписание$')
def send_msg(message):
    db = dbconn.sqldb(config.database)
    if not db.check_user(message.chat.id):
        bot.send_message(message.chat.id, 'Я еще не знаю номер вашей группы.\nНажмите на кнопку "📝 Сменить группу", чтобы задать его.')
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        today = types.InlineKeyboardButton(text="Сегодня", callback_data="today")
        yesterday = types.InlineKeyboardButton(text="Вчера", callback_data="yesterday")
        tomorrow = types.InlineKeyboardButton(text="Завтра", callback_data="tomorrow")
        anotherdayweek = types.InlineKeyboardButton(text="День недели", callback_data="dayweek")
        keyboard.add(today, yesterday, tomorrow, anotherdayweek)
        bot.send_message(message.chat.id, "Выберите день, расписание которого надо узнать:", reply_markup=keyboard)
    botan.track(config.botan_key, message.chat.id, message, '📚 Узнать расписание')



@bot.message_handler(regexp='^📝 Сменить группу$')
def change_msg(message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    y = []
    for key, value in soup.departments.items():
        y.append(types.InlineKeyboardButton(text="{}".format(value), callback_data="{}".format(key)))

    keyboard.add(*y)
    bot.send_message(message.chat.id, "Выберите свой факультет:", reply_markup=keyboard)
    botan.track(config.botan_key, message.chat.id, message, '📝 Сменить группу')

@bot.message_handler(commands=["help"])
@bot.message_handler(content_types='text')
def any_msg(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('📚 Узнать расписание')
    markup.row('📝 Сменить группу')
    bot.send_message(message.chat.id, u'Этот бот поможет вам узнать ваше расписание.\n'
                                      u'Чтобы узнать расписание, нажмите "📚 Узнать расписание" и выберите нужную дату.\n'
                                      u'Вы можете сменить группу, нажав "📝 Сменить группу" и выбрав свой факультет, курс и группу.\n', reply_markup=markup)
    botan.track(config.botan_key, message.chat.id, message, '/help or other message')


@bot.callback_query_handler(func=lambda msg: msg.data in (soup.departments.keys())) #choose course
def callback_inline(call):

    #call.data is a department

    db = dbconn.sqldb(config.database)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    k = []
    for course_rus, course_eng in db.select_course_by_department(call.data):
        k.append(types.InlineKeyboardButton(text="{}".format(course_rus), callback_data="{}".format(call.data + '+' + course_eng)))
    keyboard.add(*k)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите курс:")

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda msg: msg.data in
                                             [i + '+' + course for course in
                                              dbconn.sqldb(config.database).select_distinct_course() for i in
                                              soup.departments.keys()]) #choose group
def callback_date(call):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    groups = []
    for url, group_rus in dbconn.sqldb(config.database).select_url_groups_by_department_and_course(call.data.split('+')[0], call.data.split('+')[1]):
        groups.append(types.InlineKeyboardButton(text="{}".format(group_rus), callback_data="{}".format(url)))
    keyboard.add(*groups)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите группу:")

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda msg: msg.data in ('today','yesterday','tomorrow',
                                                          'dayweek','monday','tuesday','wednesday','thursday','friday','saturday','sunday'))
def callback_date(call):
    dayweeks = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 4: 'пятница', 5: 'суббота', 6: 'воскресенье'}
    dayweeks_eng_number = {'monday': 0, 'tuesday': 1, 'wednesday' : 2, 'thursday': 3, 'friday':4, 'saturday':5, 'sunday':6}
    dayweeks_eng_rus = {'monday': 'понедельник', 'tuesday': 'вторник',
                    'wednesday': 'среду', 'thursday': 'четверг', 'friday': 'пятницу', 'saturday': 'субботу', 'sunday': 'воскресенье'}

    db = dbconn.sqldb(config.database)
    if call.data == 'today':
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id, text =
                         '*Сегодня {0}, {1}.\n\nТекущая неделя – {2}.\n\n*Ваше расписание:\n\n'.format(
                             date.today().strftime('%d-%m-%Y'),
                             dayweeks[date.today().weekday()],
                             'знаменатель' if date.today().isocalendar()[1] % 2 == 0
                             else 'числитель')
                         + db.get_schedule(call.message.chat.id, date.today().weekday())[0][0],
                         parse_mode='Markdown')
    elif call.data == 'yesterday':
        yesterday = date.today() + timedelta(days=-1)
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id, text =
                         '*Вчерашний день: {1}, {0}.\n\nНеделя – {2}.\n\n*Расписание:\n\n'.format(
                             yesterday.strftime('%d-%m-%Y'),
                             dayweeks[yesterday.weekday()],
                             'знаменатель' if yesterday.isocalendar()[1] % 2 == 0
                             else 'числитель')
                         + db.get_schedule(call.message.chat.id, yesterday.weekday())[0][0],
                         parse_mode='Markdown')
    elif call.data == 'tomorrow':
        tomorrow = date.today() + timedelta(days=1)
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id, text =
                         '*Завтра: {1}, {0}.\n\nНеделя – {2}.\n\n*Расписание:\n\n'.format(
                             tomorrow.strftime('%d-%m-%Y'),
                             dayweeks[tomorrow.weekday()],
                             'знаменатель' if tomorrow.isocalendar()[1] % 2 == 0
                             else 'числитель')
                         + db.get_schedule(call.message.chat.id, tomorrow.weekday())[0][0],
                         parse_mode='Markdown')
    elif call.data == 'dayweek':
        dayweeks_number_eng = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday',
                               6: 'sunday'}
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        k = []
        for i in dayweeks.keys():
            k.append(types.InlineKeyboardButton(text="{}".format(dayweeks[i].capitalize()), callback_data=dayweeks_number_eng[i]))
        keyboard.add(*k)
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id, text =
                         'Выберите день недели:',
                         parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboard)


    elif call.data in ('monday','tuesday','wednesday','thursday','friday','saturday','sunday'):
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id, text =
                         'Расписание на {}:\n\n'.format(dayweeks_eng_rus[call.data])
                         + db.get_schedule(call.message.chat.id, dayweeks_eng_number[call.data])[0][0],
                         parse_mode='HTML')

@bot.callback_query_handler(func=lambda msg: msg.data in dbconn.sqldb(config.database).select_url_from_groups())  # confirm group
def callback_date(call):
    db = dbconn.sqldb(config.database)

    dep_and_group = db.select_by_url(call.data)


    if db.check_user(call.message.chat.id):
        db.update_user_schedule(call.message.chat.id,
                                call.data)
    else:
        db.insert_user_schedule(call.message.chat.id,
                                call.from_user.first_name + ("" if call.from_user.last_name is None else " " + call.from_user.last_name) + ("" if call.from_user.username is None else "  @" + call.from_user.username),
                                call.data)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Готово! Ваш факультет - {0}. Ваша группа - {1}."
                          .format(dep_and_group[0], dep_and_group[1]))



if __name__ == '__main__':
    createdb.createtables()
    soup.get_groups()
    os.makedirs('./schedule', exist_ok=True)
    updatebyschedule.sched()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print('Error occurred:')
            print(sys.stderr, str(e))
            time.sleep(10)
