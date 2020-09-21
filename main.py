from telebot import types
import sqlite3 as sql
import telebot
import time
import datetime

bot = telebot.TeleBot('1274138970:AAGGgIOK7k-Whhd8mf9qKkEGY5-S7_BjVGg')

connection = sql.connect("user.sqlite", check_same_thread=False)
q = connection.cursor()
q.execute('''
''')
connection.commit()
connection.close()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("Начать рабочий день")
    item2 = types.KeyboardButton("Закончить рабочий день")
    item3 = types.KeyboardButton("Профиль")
    item4 = types.KeyboardButton("Сменить имя")
    item5 = types.KeyboardButton("Проверить")
    markup.add(item1, item2, item3, item4, item5)
    id = message.from_user.id
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = '%s'" % (id))
    result = q.fetchall()
    if len(result) == 0:
        user_name = message.from_user.first_name
        print("Добавляем пользователя...")
        q.execute(
            "INSERT INTO user_info (Name, User_ID, Admin, Start) VALUES ('%s','%s','%s','%s')" %
                                                                                            (user_name, id, 0, 'None')
        )
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "<b>" + user_name + "</b>, Вы успешно зарегистрировались !", reply_markup=markup,
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Рады вас снова видеть, <b>" + result[0][1] + "</b> ^_^", reply_markup=markup,
                         parse_mode='html')
        connection.commit()
        connection.close()


def user_info(message):
    id = message.from_user.id
    connection = sql.connect('user.sqlite', check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    result = q.fetchall()
    if len(result) == 0:
        bot.send_message(message.chat.id, "Вы ещё не зарегистрировались ! Введите команду (начать)", parse_mode='html')
        connection.commit()
        connection.close()
    else:
        user_id = result[0][0]
        name = result[0][1]
        admin = result[0][3]
        if admin == 1:
            admin = "Администратор"
        else:
            admin = "Пользователь"
        bot.send_message(message.chat.id, "<b>Номер аккаунта: </b>" + str(user_id) + "\n<b>Имя: </b>" + name + "\n<b>Уровень привилегии: </b>" + admin, parse_mode='html')
        connection.commit()
        connection.close()


def name(message):
    body = message.text
    id = message.from_user.id
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    q.execute("UPDATE user_info SET Name='%s' WHERE User_ID = %s" % (body, id))
    bot.send_message(message.chat.id, "Ваше имя успешно изменено на: <b>" + body + "</b>", parse_mode='html')
    connection.commit()
    connection.close()


def start_day(message):
    a = datetime.datetime.now()
    b = datetime.time(a.hour, a.minute, a.second)
    id = message.from_user.id
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    result = q.fetchall()
    date = result[0][4]
    if date == 'None':
        q.execute("UPDATE user_info SET Start='%s' WHERE User_ID = %s" % (b, id))
        bot.send_message(message.chat.id,
                         "<b>" + result[0][1] + "</b>, Вы успешно начали рабочий день, желаю Вам успехов ^_^ !",
                         parse_mode='html')
        connection.commit()
        connection.close()
    else:
        bot.send_message(message.chat.id, "Для начала, закончите предыдущий день ^_^", parse_mode='html')
        connection.commit()
        connection.close()


def finish_day(message):
    date_date = datetime.date.today()
    date_finish = datetime.datetime.now()
    date_finish = datetime.time(date_finish.hour, date_finish.minute, date_finish.second)
    date_now = datetime.datetime.now()
    date_now = datetime.timedelta(hours=date_now.hour, minutes=date_now.minute, seconds=date_now.second)
    id = message.from_user.id
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    result = q.fetchall()
    user_id = result[0][0]
    name = result[0][1]
    date = result[0][4]
    q.execute("SELECT * FROM list WHERE User_id = %s AND Date = '%s'" % (user_id, str(date_date)))
    result = q.fetchall()
    if date == 'None':
        bot.send_message(message.chat.id, "Вы ещё не начали рабочий день, чтобы закончить его ^_^", parse_mode='html')
        connection.commit()
        connection.close()
    else:
        a, b, c = date.split(':')
        date_two = datetime.timedelta(hours=int(a), minutes=int(b), seconds=int(c))
        date_sum = date_now - date_two
        q.execute("UPDATE user_info SET Start='%s' WHERE User_ID = %s" % ('None', id))
        if len(result) == 0:
            q.execute("INSERT INTO list (User_id, Start, Finish, Sum, Date) VALUES ('%s','%s','%s','%s','%s')" % (user_id, date, date_finish, date_sum, date_date))
        else:
            date_list = result[0][4]
            a, b, c = date_list.split(':')
            date_list = datetime.timedelta(hours=int(a), minutes=int(b), seconds=int(c))
            date_sum = date_sum + date_list
            q.execute("UPDATE list SET Sum='%s' WHERE User_id = %s AND Date = '%s'" % (date_sum, user_id, str(date_date)))
            q.execute("UPDATE list SET Finish='%s' WHERE User_id = %s AND Date = '%s'" % (date_finish, user_id, str(date_date)))
        bot.send_message(message.chat.id, "<b>" + name + "</b>, за сегодняшний день Вы отработали: <b>" + str(date_sum) + "</b>", parse_mode='html')
        connection.commit()
        connection.close()


def admin(message):
    body = message.text
    id = message.from_user.id
    Itog = ''
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    result = q.fetchall()
    q.execute("SELECT * FROM user_info WHERE id = %s" % (body))
    result = q.fetchall()
    Name = result[0][1]
    q.execute("SELECT * FROM list WHERE User_id = %s" % (body))
    result = q.fetchall()
    if len(result) == 0:
        bot.send_message(message.chat.id, "Такого пользователя не существует или данные по его работе отсутствуют !", parse_mode='html')
        connection.commit()
        connection.close()
    else:
        for i in result:
            Start = i[2]
            Finish = i[3]
            Sum = i[4]
            Date = i[5]
            Itog += "\n<b>Пользователь: </b>" + Name + "\n<b>Начал рабочий день: </b>" + Start + "\n<b>Закончил рабочий день: </b>" + Finish + "\n<b>Отработал: </b>" + Sum + "\n<b>Дата: </b>" + Date + "\n"
        bot.send_message(message.chat.id, Itog, parse_mode='html')
        connection.commit()
        connection.close()


def admin_date(message):
    body = message.text
    id = message.from_user.id
    Itog = ''
    connection = sql.connect("user.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute("SELECT * FROM user_info WHERE User_ID = %s" % (id))
    result = q.fetchall()
    q.execute("SELECT * FROM user_info WHERE id = %s" % (body))
    result = q.fetchall()
    Name = result[0][1]
    q.execute("SELECT * FROM list WHERE User_id = %s" % (body))
    result = q.fetchall()
    if len(result) == 0:
        bot.send_message(message.chat.id, "Такого пользователя не существует или данные по его работе отсутствуют !", parse_mode='html')
        connection.commit()
        connection.close()
    else:
        for i in result:
            Start = i[2]
            Finish = i[3]
            Sum = i[4]
            Date = i[5]
            Itog += "\n<b>Пользователь: </b>" + Name + "\n<b>Начал рабочий день: </b>" + Start + "\n<b>Закончил рабочий день: </b>" + Finish + "\n<b>Отработал: </b>" + Sum + "\n<b>Дата: </b>" + Date + "\n"
        bot.send_message(message.chat.id, Itog, parse_mode='html')
        connection.commit()
        connection.close()


@bot.message_handler(content_types=['text'])
def main(message):
    body = message.text
    if body.lower() == 'профиль':
        user_info(message)
    elif body.lower() == 'сменить имя':
        msg = bot.send_message(message.chat.id, "Введите новое имя")
        bot.register_next_step_handler(msg, name)
    elif body.lower() == 'начать рабочий день':
        start_day(message)
    elif body.lower() == 'закончить рабочий день':
        finish_day(message)
    elif body.lower() == 'проверить':
        msg = bot.send_message(message.chat.id, "Введите id пользователя")
        bot.register_next_step_handler(msg, admin)


while True:
    try:
        while True:
            try:
                # RUN
                bot.polling(none_stop=True)
            except:
                time.sleep(1)
    except: bot.polling(none_stop=True)