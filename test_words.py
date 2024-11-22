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

#button.add(types.InlineKeyboardButton('', callback_data=''))
#bot.send_message(message.chat.id, '')
#bot.send_message(message.chat.id, '')

def insert(message):
    global conn, cursor, idn
    idn = message.from_user.username
    conn = sqlite3.connect('base.bd')
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {idn} 
                   (new_words TEXT, 
                   data_new_words DATA, 
                   data_next_rep DATA, 
                   amount_of_rep INTEGER, 
                   complete_words TEXT)')
    conn.commit()

def curr_date():
    global current_date
    current_date = datetime.datetime.now().strftime("%d.%m.%y %I:%M:%S PM")
    

'''КОМАДНА /WORDS'''
@bot.message_handler(commands=['words'])
def words(message):
    bot.send_message(message.chat.id, 'Введіть слово, яке хочете добавити (або "end", щоб завершити): ')
    # Встановлюємо обробник для відповідей
    bot.register_next_step_handler(message, process_words)

# Функція для ДОДАВАННЯ НОВИХ СЛІВ
def process_words(message):
    if message.text.lower() == 'end':
        # Команда "end" завершує введення слів
        show_words(message)
    else:
        insert(message)
        cursor.execute(f'SELECT new_words FROM {idn} WHERE new_words = ?', (message.text,))
        existing_word = cursor.fetchone()

        if existing_word:
            bot.send_message(message.chat.id, f'Слово "{message.text}" вже є в базі даних.')
        else:
            # Додаємо слово до бази даних
            curr_date()
            cursor.execute(f'INSERT INTO {idn} (new_words, data_new_words, amount_of_rep,) VALUES (?, ?, ?)', (message.text, current_date, 0,))
            conn.commit()
            # Повідомлення про успішне додавання слова
            bot.send_message(message.chat.id, f'Слово "{message.text}" успішно збережено.')
            # Запит на введення наступного слова
        bot.send_message(message.chat.id, 'Введіть ще одне слово (або "end", щоб завершити): ')
        # Встановлюємо обробник для наступного слова
        bot.register_next_step_handler(message, process_words)

# Функція для ВІДОБРАЖЕННЯ ДОДАНИХ СЛІВ СЬОГОДНІ
@bot.message_handler(commands=['added_today'])
def show_words(message):
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words FROM {idn} WHERE complete_words IS NULL AND data_new_words = {current_date}')
    data = cursor.fetchall()
    words = [word[0] for word in data]
    if words and all(word is not None and isinstance(word, str) for word in words):
        # Відправляємо слова, якщо вони були додані
        bot.send_message(message.chat.id, f'Слова, які ви добавили сьогодні:\n' + '\n'.join(words))
    else:
        # Відправляємо повідомлення, якщо сьогодні не було доданих слів
        bot.send_message(message.chat.id, 'На жаль, сьогодні ви не додали жодного слова.')
    # Дізнаюсь який сьогодні день з 365
    daysend = current_date.timetuple().tm_yday
    goal = 300
    button = types.InlineKeyboardMarkup()
    button.add(types.InlineKeyboardButton('Повторити слова', callback_data='rep_word'))


    cursor.execute(f'SELECT complete_words FROM {idn} WHERE new_words IS NULL')
    complete = cursor.fetchall()
    bot.send_message(message.chat.id, '///Можливість створення власних цілей, у розробці///')
    words = [word[0] for word in complete]
    bot.send_message(message.chat.id, 'Твоя ціль вчити 5 слів у день. Тоді ти зможеш до кінця року вивчити більше ніж 300 слів😍😘\n Приблизно за 60 днів🥳 \n Слова треба повторювати і ти це будеш робити 5 разів для слова, а також будеш придумувати до нього речення.')
    bot.send_message(message.chat.id, f'До кінця року <b>{str(365 - int(daysend))}</b>', parse_mode='html')

    bot.send_message(message.chat.id, f'Кількість вивчених слів: <b>{str(len(words))}</b>', parse_mode='html')
    bot.send_message(message.chat.id, f'Ще треба вивчити слів: <b>{str(int(goal)-int(len(words)))}</b>', parse_mode='html', reply_markup=button)
    cursor.close()
    conn.close()

#ПОКАЗАТИ, ТЕ ЩО ВЧИШ
@bot.message_handler(commands=['learn'])
def new_words(message):
    insert(message)
    cursor.execute(f'SELECT new_words, data_next_rep, amount_of_rep FROM {idn} WHERE complete_words IS NULL')
    complete = cursor.fetchall()
    for row in complete:
        wordo = row[0]
        data_next_repeat = row[1]
        amount = row[2]

    message_text = (f"Слово: {wordo}\n"
                    f"Наступне повторення: {data_next_repeat}\n"
                    f"Кількість повторень: {amount}\n"
                    "__________")
    # Об'єднання заголовка та рядків для виведення
    bot.send_message(message.chat.id, f'Слова, які ти вчиш:\n{message_text}')

#ПОКАЗАТИ ТЕ, ЩО МОЖНА СЬОГОНІ ПОВТОРИТИ
@bot.message_handler(commands=['rep_word'])
def repeat_words(message):
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words FROM {idn} WHERE complete_words IS NULL AND data_next_rep = {current_date}')
    complete = cursor.fetchall()
    words = [word[0] for word in complete]
    """
    Explain:
    complete = [('cat',), ('dog',), ('mouse',)]
    
    words = ['cat', 'dog', 'mouse']
    """
    
    if complete:
        bot.send_message(message.chat.id, 'Ось усі слова, які ви можете сьогодні повторити:<b>\n' + '\n</b>'.join(words), parse_mode='html')
        bot.send_message(message.chat.id, 'Памʼятай, у бота тобі нічого писати не треба (можливо це тимчасово 🤷‍♂️). Я надаю тобі підказки, яким чином буде ефективно повторити слово, яке є на черзі. \nКоли ти їх виконаєш і тільки тоді, ти можеш вказати, що успішно повторив слово (тобто нажати True❤️). \nЯкщо ж ти слово не згадав, дотримуйся підказок для повторення, і вибери False💔.')    
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton('Почати повторення', callback_data='start_rep_word'))
    else:
        bot.send_message(message.chat.id, 'Сьогодні немає слів для вивчення :( \nповертайся завтра або переглянь усі слова, які ти вивчаєш :)')    
  
@bot.message_handler(commands=['start_rep_word'])
def start_repeat_words(message):
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words FROM {idn} WHERE complete_words IS NULL AND data_next_rep = {current_date}')
    complete = cursor.fetchall()
    wordso = [word[0] for word in complete]
    # worder копія щоб wordso залишилось цілим, і можна було вивести кількість повторених слів.
    worder = wordso.copy()
    bot.send_message(message.chat.id, 'Інструкція: Якщо ти памʼятаєш переклад цього слова напиши 4 речення з ним. (///beta_text!///)')
    foo(message)

stat_false = []
def foo(message): 
    global one_word, stat_false
    #для запису скільки незгадав і скільки згадав
    
    if message.text.lower() == 'end' or len(worder) == 0:
        bot.send_message(message.chat.id, f'Молодець! Ти чудово постарався. Сьогодні ти повторив {str(len(wordso))} слів🥳 \n{str(len(wordso) - len(stat_false))} слова ти згадав та {str(len(stat_false))} не згадав. \nЧекаю тебе завтра або в будь-який інший час❤️')
        del one_word
        del stat_false
        return
    elif len(wordso):
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton('True❤️', callback_data='true'))
        button.add(types.InlineKeyboardButton('False💔', callback_data='false'))
        
        one_word = worder.pop(0)
        bot.send_message(message.chat.id, f'Чи памʼятаєш ти це слово? \n\n<b>{one_word}</b>', parse_mode='html', reply_markup=button)
    else:
        bot.send_message(message.from_user.id, 'Ти ще не додав жодного слова, яке можна почати вчити.')



    







'''ПОВТОРЕННЯ СЛІВ БЕЗ ЗАРАХУВАННЯ, ПРОСТО ДЛЯ ПРОФІЛАКТИКИ!'''
@bot.message_handler(commands=['teach'])
def teach(message):
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words FROM {idn}')
    global wordso, worder
    complete = cursor.fetchall()
    wordso = [word[0] for word in complete]
    # worder копія щоб wordso залишилось цілим, і можна було вивести кількість повторених слів.
    worder = wordso.copy()
    bot.send_message(message.chat.id, 'Інструкція: Якщо ти памʼятаєш переклад цього слова напиши 4 речення з ним. (///beta_text!///)')
    foo(message)

stat_false = []
def foo(message): 
    global one_word, stat_false
    #для запису скільки незгадав і скільки згадав
    
    if message.text.lower() == 'end' or len(worder) == 0:
        bot.send_message(message.chat.id, f'Молодець! Ти чудово постарався. Сьогодні ти повторив {str(len(wordso))} слів🥳 \n{str(len(wordso) - len(stat_false))} слова ти згадав та {str(len(stat_false))} не згадав. \nЧекаю тебе завтра або в будь-який інший час❤️')
        del one_word
        del stat_false
        return
    elif len(wordso):
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton('True❤️', callback_data='tru'))
        button.add(types.InlineKeyboardButton('False💔', callback_data='false'))
        
        one_word = worder.pop(0)
        bot.send_message(message.chat.id, f'Чи памʼятаєш ти це слово? \n\n<b>{one_word}</b>', parse_mode='html', reply_markup=button)
    else:
        bot.send_message(message.from_user.id, 'Ти ще не додав жодного слова, яке можна почати вчити.')



'''CALLBACK ДЛЯ BCIX КНОПОК'''
@bot.callback_query_handler(func=lambda callback: True)
def call_message(callback):
    if callback.data == 'start_rep_word':
      start_repeat_words(callback)
    elif callback.data == 'rep_word':
      repeat_words(callback)
    elif callback.data == 'true':
      bot.send_message(callback.message.chat.id, 'Молодець! Це слово було повторено)')
      insert(callback)
      curr_date()
      cursor.execute(f'SELECT amount_of_rep FROM {idn} WHERE new_words = ?', (one_word,))
      amount_rep = [i[0] for i in cursor.fetchone()]
      next_rep = amount_rep+2
      data_next_rep = current_date + datetime.timedelta(days=next_rep)
      cursor.execute(f'UPDATE {idn} SET data_next_rep = {data_next_rep.strftime("%d/%m/%Y")}, amount_of_rep += 1 WHERE new_words = {one_word}')
      conn.commit
      foo(callback.message)
    elif callback.data == 'false':
      bot.send_message(callback.message.chat.id, 'Що ж, чим більше ти помиляєшся, тим кращим буде кінцевий результат.')
      worder.insert(len(worder)-1, one_word)
      #Додати цілі слова, аби потім додати функцію перегляду, які слова згадав, а які ні
      if one_word not in stat_false:
        stat_false.append(one_word)
      foo(callback.message)
    elif callback.data == 'tru':
      bot.send_message(callback.message.chat.id, 'Молодець! Це слово було повторено❤️')
      foo(callback.message)




bot.infinity_polling()