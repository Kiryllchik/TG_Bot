import logging
import telebot
from telebot import types
import datetime
import time
import sqlite3
from keep_alive import keep_alive

keep_alive()
logging.basicConfig(level = logging.INFO)

bot = telebot.TeleBot('6646599481:AAGmgYzg4ycfTJDjOAjgKr8MMeoGm8PTWf4')


def insert(message):
    global conn, cursor, idn
    idn = message.from_user.username
    conn = sqlite3.connect('base.bd')
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {idn} (new_words TEXT, data_new_words TEXT, complete_words TEXT)')
    conn.commit()


current_date = datetime.datetime.now()



"""НАВЧАЛЬНА CXEMA /GOO"""
@bot.message_handler(commands=['goo'])
def scheme_learn(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Python', callback_data='python'))
    markup.add(types.InlineKeyboardButton('Англійська мова', callback_data='english'))
    
    bot.send_message(message.chat.id, 'Давай розпочнемо навчання за твоєю схемою)\n Спочатку обери з чого ти розпочнеш:', reply_markup=markup)

def answer(message):
    current_date
    minut = 30
    conn = sqlite3.connect('base.bd')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO {idn} (begin) VALUES (?)', (current_date))
    conn.commit()
    bot.send_message(message.chat.id, f'Отже час початку навчання: {current_date.strftime("%d.%m.%y %H:%M:%S")}')
    bot.send_message(message.chat.id, f'Перше з чого варто почати, це з вивчення нової теорії. Можеш щось записувати, але лише загалом.\n Стандартний час {minut} хв. Його можна збільшити або зменишити.', reply_markup=markup)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Змінити стандартний час ', callback_data='ch_time'))
    

    

    
def question(message):
    bot.send_message(message.chat.id, 'Від початку твого навчання пройшло вже 30хв, чи хочеш ти закінчити теоретичну частину і перейти до наступного етапу?')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти до наступного етапу', callback_data='next_step'))
    markup.add(types.InlineKeyboardButton('Запитати пізніше', callback_data='later'))

def rest(message):
    pass



@bot.callback_query_handler(func=lambda callback: callback.data == 'python' or 'english')
def scheme_learn_callback(callback):
    pass
def answer_callback(callback):
    minut = 30
    need_time = current_date + datetime.timedelta(minutes=minut)
    while current_date != need_time:
        time.sleep(60)
        continue
    

def question_callback(callback):
    pass








bot.infinity_polling()