from collections.abc import Awaitable
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import datetime
import locale
import sqlite3
import asyncio
from aiocron import crontab
from keep_alive import keep_alive

keep_alive()
logging.basicConfig(level = logging.INFO)
locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')


bot = Bot(token='6622901001:AAGf_74CHhEbyizls_qRJgHwoO6FCng3Im4')
dp = Dispatcher(bot=bot)


def curr_date():
  global current_date
  current_date = datetime.datetime.now()
  
def insert(message):
  global conn, cursor, idn
  idn = message.from_user.username
  conn = sqlite3.connect('base.bd')
  cursor = conn.cursor()
  cursor.execute(f'''CREATE TABLE IF NOT EXISTS {idn} 
                 (new_words TEXT, 
                 data_new_words DATA, 
                 data_next_rep DATA, 
                 amount_of_rep INTEGER, 
                 complete_words INTEGER)''')
  conn.commit()
  
  
@dp.message()
async def id_user(message):
    global chat_id, info_user
    if not chat_id: # чи парацює if?
        chat_id = message.chat.id 
        info_user = message.from_user
        


'''
 КОМАНДА /START
'''
@dp.message(CommandStart(['start'])) 
async def start(message): 
    await message.answer(f'Привіт, {message.from_user.username}❤️! Все ще памʼятаєш про мене? 🥹')
    await message.answer('Тоді рушаймо до зросту📈📈 😁')
    # Кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Розклад пар 🗓️', callback_data='data'))
    markup.add(types.InlineKeyboardButton('Англійська мова', callback_data='english'))
    markup.add(types.InlineKeyboardButton('///Повторити власні конспекти///', callback_data='repeat'))
    markup.add(types.InlineKeyboardButton('///Навчання. Фундаментальний метод.///', callback_data='studying'))
    # Повідомлення 3
    await message.answer(chat_id, 'Що ти хочеш зробити?', reply_markup=markup)

'''
''' 







if __name__ == '__main__':
   dp.start_polling(bot)