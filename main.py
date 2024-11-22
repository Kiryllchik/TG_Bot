from collections.abc import Awaitable
import logging
import telebot
from telebot import types
import datetime
import locale
import sqlite3
import asyncio
from aiocron import crontab
from keep_alive import keep_alive

keep_alive()
logging.basicConfig(level=logging.INFO)
#locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')

bot = telebot.TeleBot('6646599481:AAFzQo1xgauCXLmXQnJBTBKmZHCae0FHUPs')


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


def curr_date():
    global current_date
    current_date = datetime.datetime.now()
    #("%d/%m/%Y")


def id_user(message):
    global chat_id, info_user
    chat_id = message.from_user.id
    info_user = message


'''
 КОМАНДА /START
'''


@bot.message_handler(commands=['start'])
def start(message):

    id_user(message)
    bot.send_message(
        chat_id,
        f'Привіт, {message.from_user.username}❤️! Все ще памʼятаєш про мене? 🥹'
    )
    # Повідомлення 2
    bot.send_message(chat_id, 'Тоді рушаймо до зросту📈📈 😁')
    # Кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Розклад пар 🗓️', callback_data='data'))
    markup.add(
        types.InlineKeyboardButton('Англійська мова', callback_data='english'))
    markup.add(
        types.InlineKeyboardButton('///Повторити власні конспекти///',
                                   callback_data='repeat'))
    markup.add(
        types.InlineKeyboardButton('///Навчання. Фундаментальний метод.///',
                                   callback_data='studying'))
    # Повідомлення 3
    bot.send_message(chat_id, 'Що ти хочеш зробити?', reply_markup=markup)


'''
'''
'''ДАНІ ДЛЯ КОМАНДИ /DATA'''
# Отримуємо поточну дату
current_dato = datetime.datetime.now()
tomorrow = current_dato + datetime.timedelta(days=1)
# Виводимо назву сьогоднішнього дня
day_name = tomorrow.strftime("%A")
# Визначаємо номер дня тижня (понеділок - 0, вівторок - 1, ..., неділя - 6)
day_of_week = current_dato.weekday()
day_of_week += 1

# Список посилань на фото для кожного дня тижня
photos = [
    './photo/monday.jpg',
    './photo/tuesday.jpg',
    './photo/wednesday.jpg',
    './photo/thursday.jpg',
    './photo/friday.jpg',
]
# Для вибору іншого дня в /DATA
calendar = ['понеділок', 'вівторок', 'середа', 'четвер', 'пʼятниця']
'''
КОМАНДА /DATA
'''


# Обробник для команди /data
@bot.message_handler(commands=['data'])
def daily_photo(message):
    id_user(message)
    if 0 <= day_of_week < len(photos):
        # Відправляємо фото відповідно до дня тижня
        bot.send_message(chat_id,
                         f'Розклад пар у <b>{day_name.upper()}</b>',
                         parse_mode='html')
        bot.send_photo(chat_id, open(photos[day_of_week], 'rb'))

        # Створюємо клавіатуру для вибору іншого дня
        markup = types.InlineKeyboardMarkup()
        for i in range(5):
            markup.add(
                types.InlineKeyboardButton(calendar[i].upper(),
                                           callback_data=calendar[i]))
        bot.send_message(chat_id,
                         "Можливо інший день: ☺️",
                         reply_markup=markup)
    else:
        # Повторюєм цикл оскільки в if він не спрацьовує коли активується else
        markup = types.InlineKeyboardMarkup()
        for i in range(5):
            markup.add(
                types.InlineKeyboardButton(calendar[i].upper(),
                                           callback_data=calendar[i]))
        bot.send_message(chat_id,
                         f'Розклад пар у <b>ПОНЕДІЛОК</b>',
                         parse_mode='html')
        bot.send_photo(chat_id, open(photos[0], 'rb'))

        bot.send_message(chat_id,
                         "Можливо інший день: ☺️",
                         reply_markup=markup)


'''
'''
'''CALLBACK ДЛЯ КНОПОК В /DATA'''


# Обробник для вибору іншого дня з клавіатури
@bot.callback_query_handler(func=lambda callback: callback.data in calendar)
def callback_daily_photo(callback):
    selected_day = callback.data
    # Виклик фунції, яка надсилає фото вибораного дня

    set_daily_photo(callback.message, selected_day)


    #set_daily_photo, який приймає обраний день і виводить фото
def set_daily_photo(message, selected_day=None):
    if selected_day in calendar:
        markup = types.InlineKeyboardMarkup()
        for i in range(5):
            markup.add(
                types.InlineKeyboardButton(calendar[i].upper(),
                                           callback_data=calendar[i]))

        selected_day_index = calendar.index(selected_day)
        bot.send_message(
            message.chat.id,
            f'Розклад пар у <b>{calendar[selected_day_index].upper()}</b>',
            parse_mode='html')
        bot.send_photo(message.chat.id,
                       open(photos[selected_day_index], 'rb'),
                       reply_markup=markup)


'''
КОМАНДА /REPEAT
'''


@bot.message_handler(commands=['repeat'])
def repeat(message):
    id_user(message)
    # Цикл створення кнопок для позначення дня місяця

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    month = 31
    row = []
    for i in range(1, month):
        button = types.InlineKeyboardButton(f'{str(i)}.10.🕰️',
                                            callback_data=str(i))
        row.append(button)
        # Додавання < та >
        if i == 28:
            btn_left = (types.InlineKeyboardButton('<', callback_data='left'))
            btn_right = (types.InlineKeyboardButton('>',
                                                    callback_data='right'))
            row.append(btn_left)
        elif i == 30:
            row.append(btn_right)
    keyboard.add(*row)

    # Надсилання повідомлення
    bot.send_message(chat_id,
                     'Ось які завдання тобі доступні сьогодні: 😘',
                     reply_markup=keyboard)


'''
'''
numbers = []
for i in range(30):
    numbers.append(str(i))
'''РОЗДІЛ АНГЛІЙСКА МОВА.
   ТУТ БОТ ДОПОМАГАТИМЕ ЗАПАМЯТОВУВАТИ АНГЛІЙСЬКІ СЛОВА'''


@bot.message_handler(commands=['english'])
def english_form(message):
    id_user(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Додати нові слова', callback_data='words'))
    markup.add(types.InlineKeyboardButton('Всі слова', callback_data='learn'))
    markup.add(
        types.InlineKeyboardButton('Слова додані сьогодні',
                                   callback_data='added_today'))
    markup.add(
        types.InlineKeyboardButton('Повторити слова на сьогодні',
                                   callback_data='rep_word'))
    markup.add(
        types.InlineKeyboardButton('Повторення без запису',
                                   callback_data='teach'))
    markup.add(
        types.InlineKeyboardButton('Вивчені слова', callback_data='complete'))

    bot.send_message(chat_id,
                     'Виберіть дію для англійської мови',
                     reply_markup=markup)


@crontab('* 12 * *')
async def time_message():
    global chat_id
    if chat_id:
        await bot.send_message(
            chat_id,
            'Моє серденько❤️, Are you ready for RISE!? \nLet`s start!')
        await bot.send_message(chat_id, 'Надсилай /rep_word i погнали😉')


'''КОМАДНА /WORDS'''


@bot.message_handler(commands=['words'])
def words(message):
    id_user(message)
    bot.send_message(
        chat_id,
        'Введіть слово, яке хочете добавити (або "end", щоб завершити): ')
    # Встановлюємо обробник для відповідей
    bot.register_next_step_handler(message, process_words)


# Функція для ДОДАВАННЯ НОВИХ СЛІВ
def process_words(message):
    if message.text.lower() == 'end':
        # Команда "end" завершує введення слів
        show_words(message)
    else:
        insert(message)
        cursor.execute(f'SELECT new_words FROM {idn} WHERE new_words = ?',
                       (message.text, ))
        existing_word = cursor.fetchone()

        if existing_word:
            bot.send_message(chat_id,
                             f'Слово "{message.text}" вже є в базі даних.')
        else:
            # Додаємо слово до бази даних
            curr_date()
            next_dat = (current_date +
                        datetime.timedelta(days=1)).strftime("%d/%m/%Y")
            cursor.execute(
                f'INSERT INTO {idn} (new_words, data_new_words, data_next_rep, amount_of_rep) VALUES (?, ?, ?, ?)',
                (message.text, current_date.strftime("%d/%m/%Y"), next_dat, 0))
            conn.commit()
            # Повідомлення про успішне додавання слова
            bot.send_message(chat_id,
                             f'Слово "{message.text}" успішно збережено.')
            # Запит на введення наступного слова
        bot.send_message(chat_id,
                         'Введіть ще одне слово (або "end", щоб завершити): ')
        # Встановлюємо обробник для наступного слова
        bot.register_next_step_handler(message, process_words)


# Функція для ВІДОБРАЖЕННЯ ДОДАНИХ СЛІВ СЬОГОДНІ
@bot.message_handler(commands=['added_today'])
def show_words(message):
    id_user(message)
    insert(message)
    curr_date()
    cursor.execute(
        f'SELECT new_words FROM {idn} WHERE complete_words IS NULL AND data_new_words = ?',
        (current_date.strftime("%d/%m/%Y"), ))

    data = cursor.fetchall()
    words = [word[0] for word in data]
    if words and all(word is not None and isinstance(word, str)
                     for word in words):
        # Відправляємо слова, якщо вони були додані
        bot.send_message(
            chat_id, f'Слова, які ви добавили сьогодні:\n' + '\n'.join(words))
    else:
        # Відправляємо повідомлення, якщо сьогодні не було доданих слів
        bot.send_message(chat_id,
                         'На жаль, сьогодні ви не додали жодного слова.')
    # Дізнаюсь який сьогодні день з 365
    daysend = current_dato.timetuple().tm_yday
    goal = 300
    button = types.InlineKeyboardMarkup()
    button.add(
        types.InlineKeyboardButton('Повторити слова', callback_data='teach'))

    cursor.execute(f'SELECT complete_words FROM {idn} WHERE new_words IS NULL')
    complete = cursor.fetchall()
    bot.send_message(chat_id,
                     '///Можливість створення власних цілей, у розробці///')
    words = [word[0] for word in complete]
    bot.send_message(
        chat_id,
        'Твоя ціль вчити 5 слів у день. Тоді ти зможеш до кінця року вивчити більше ніж 300 слів😍😘\n Приблизно за 60 днів🥳 \n Слова треба повторювати і ти це будеш робити 5 разів для слова, а також будеш придумувати до нього речення.'
    )
    bot.send_message(chat_id,
                     f'До кінця року <b>{str(365 - int(daysend))}</b>',
                     parse_mode='html')

    bot.send_message(chat_id,
                     f'Кількість вивчених слів: <b>{str(len(words))}</b>',
                     parse_mode='html')
    bot.send_message(
        chat_id,
        f'Ще треба вивчити слів: <b>{str(int(goal)-int(len(words)))}</b>',
        parse_mode='html',
        reply_markup=button)
    cursor.close()
    conn.close()


#ПОКАЗАТИ, ТЕ ЩО ВЧИШ
@bot.message_handler(commands=['learn'])
def new_words(message):
    id_user(message)
    insert(message)
    cursor.execute(
        f'SELECT new_words, data_new_words, data_next_rep, amount_of_rep FROM {idn}'
    )
    complete = cursor.fetchall()

    message_text = ""
    for row in complete:
        wordo = row[0]
        data_creat = row[1]
        data_next_repeat = row[2]
        amount = row[3]
        message_text += (f"Слово: <b>{wordo}</b>\n"
                         f"Дата додавання: {data_creat}\n"
                         f"Наступне повторення: {data_next_repeat}\n"
                         f"Кількість повторень: <b>{amount}/6</b>\n"
                         "__________\n\n\n")

    # Об'єднання заголовка та рядків для виведення
    bot.send_message(chat_id,
                     f'Слова, які ти вчиш:\n{message_text}',
                     parse_mode='html')


#ПОКАЗАТИ ТЕ, ЩО МОЖНА СЬОГОНІ ПОВТОРИТИ
@bot.message_handler(commands=['rep_word'])
def repeat_words(message):
    id_user(message)
    insert(message)
    curr_date()
    global wordso, worder
    cursor.execute(f'SELECT new_words, data_next_rep FROM {idn}')
    complete = cursor.fetchall()
    # worder копія щоб wordso залишилось цілим, і можна було вивести кількість повторених слів.
    global selected_words
    selected_words = []
    for row in complete:
        db_date = datetime.datetime.strptime(
            row[1], "%d/%m/%Y")  # Перетворення рядка у datetime
        if db_date <= current_date:
            selected_words.append(row[0])

    if complete:
        button = types.InlineKeyboardMarkup()
        button.add(
            types.InlineKeyboardButton('Почати повторення',
                                       callback_data='start_rep_word'))
        bot.send_message(
            chat_id,
            'Ось слова, які ти можеш повторити сьогодні:\n' +
            '\n'.join([f'<b>{word}</b>' for word in selected_words]),
            parse_mode='html',
            reply_markup=button)
        bot.send_message(
            chat_id,
            'Памʼятай, у бота тобі нічого писати не треба (можливо це тимчасово 🤷‍♂️). Я надаю тобі підказки, яким чином буде ефективно повторити слово, яке є на черзі. \nКоли ти їх виконаєш і тільки тоді, ти можеш вказати, що успішно повторив слово (тобто нажати True❤️). \nЯкщо ж ти слово не згадав, дотримуйся підказок для повторення, і вибери False💔.'
        )

    else:
        bot.send_message(
            chat_id,
            'Сьогодні немає слів для вивчення :( \nПовертайся завтра або переглянь усі слова, які ти вивчаєш :)'
        )


'''ПОЧАТИ ВИВЧЕННЯ СЛІВ НА СЬОГОДНІ'''


@bot.message_handler(commands=['start_rep_word'])
def start_repeat_words(message):
    id_user(message)
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words, data_next_rep FROM {idn}')
    complete = cursor.fetchall()
    # worder копія щоб wordso залишилось цілим, і можна було вивести кількість повторених слів.
    global selected_words, worder
    selected_words = []
    for row in complete:
        db_date = datetime.datetime.strptime(
            row[1], "%d/%m/%Y")  # Перетворення рядка у datetime
        if db_date <= current_date:
            selected_words.append(row[0])
    if complete:
        worder = selected_words.copy()
        bot.send_message(
            chat_id,
            'Інструкція: Якщо ти памʼятаєш переклад цього слова напиши 4 речення з ним. (///beta_text!///)'
        )
        foo(message)
    else:
        bot.send_message(
            chat_id, 'Ти ще не додав жодного слова, яке можна почати вчити.')


stat_false = []


def foo(message):
    global one_word, stat_false
    #для запису скільки незгадав і скільки згадав

    if len(worder) == 0:
        bot.send_message(
            chat_id,
            f'Молодець! Ти чудово постарався. Сьогодні ти повторив {str(len(selected_words))} слів🥳 \n{str(len(selected_words) - len(stat_false))} слова ти згадав та {str(len(stat_false))} не згадав. \nЧекаю тебе завтра або в будь-який інший час❤️'
        )
        del one_word
        del stat_false
        return
    elif len(selected_words):
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton('True❤️', callback_data='true'))
        button.add(types.InlineKeyboardButton('False💔', callback_data='false'))

        one_word = worder.pop(0)
        bot.send_message(chat_id,
                         f'Чи памʼятаєш ти це слово? \n\n<b>{one_word}</b>',
                         parse_mode='html',
                         reply_markup=button)
        if message.text.lower() == 'end':
            bot.send_message(
                chat_id,
                f'Молодець! Ти чудово постарався. Сьогодні ти повторив {str(len(wordso))} слів🥳 \n{str(len(selected_words) - len(stat_false))} слова ти згадав та {str(len(stat_false))} не згадав. \nЧекаю тебе завтра або в будь-який інший час❤️'
            )
            del one_word
            del stat_false
            return
    else:
        bot.send_message(
            chat_id, 'Ти ще не додав жодного слова, яке можна почати вчити.')


'''СЛОВА, ЯКІ ТИ ВИВЧИВ'''


@bot.message_handler(commands=['complete'])
def complete_word(message):
    id_user(message)
    insert(message)
    cursor.execute(f'SELECT new_words FROM {idn} WHERE complete_words = 1')
    complete = cursor.fetchall()
    words = [word[0] for word in complete]
    if complete:
        bot.send_message(chat_id,
                         'Ось слова, які ти ВИВЧИВ: \n' + '\n'.join(words))
    else:
        bot.send_message(chat_id, 'Нажаль ти ще не вивчив жодного слова')


'''ПОВТОРЕННЯ СЛІВ БЕЗ ЗАРАХУВАННЯ, ПРОСТО ДЛЯ ПРОФІЛАКТИКИ!'''


@bot.message_handler(commands=['teach'])
def teach(message):
    id_user(message)
    insert(message)
    curr_date()
    cursor.execute(f'SELECT new_words FROM {idn}')
    global wordso, worder
    complete = cursor.fetchall()
    wordso = [word[0] for word in complete]
    # worder копія щоб wordso залишилось цілим, і можна було вивести кількість повторених слів.
    worder = wordso.copy()
    bot.send_message(
        chat_id,
        'Інструкція: Якщо ти памʼятаєш переклад цього слова напиши 4 речення з ним. (///beta_text!///)'
    )
    foos(message)


stat_false = []


def foos(message):
    global one_word, stat_false
    #для запису скільки незгадав і скільки згадав

    if message.text.lower() == 'end' or len(worder) == 0:
        bot.send_message(
            chat_id,
            f'Молодець! Ти чудово постарався. Сьогодні ти повторив {str(len(wordso))} слів🥳 \n{str(len(wordso) - len(stat_false))} слова ти згадав та {str(len(stat_false))} не згадав. \nЧекаю тебе завтра або в будь-який інший час❤️'
        )
        del one_word
        del stat_false
        return
    elif len(wordso):
        button = types.InlineKeyboardMarkup()
        button.add(types.InlineKeyboardButton('True❤️', callback_data='tru'))
        button.add(types.InlineKeyboardButton('False💔', callback_data='fals'))

        one_word = worder.pop(0)
        bot.send_message(chat_id,
                         f'Чи памʼятаєш ти це слово? \n\n<b>{one_word}</b>',
                         parse_mode='html',
                         reply_markup=button)
    else:
        bot.send_message(
            chat_id, 'Ти ще не додав жодного слова, яке можна почати вчити.')


'''CALLBACK ДЛЯ BCIX КНОПОК'''


@bot.callback_query_handler(func=lambda callback: True)
def call_message(callback):
    if callback.data == 'start_rep_word':
        start_repeat_words(info_user)

    elif callback.data == 'rep_word':
        repeat_words(callback)
    elif callback.data == 'true':
        bot.send_message(chat_id, 'Молодець! Це слово було повторено)')
        insert(callback)
        curr_date()
        cursor.execute(f'SELECT amount_of_rep FROM {idn} WHERE new_words = ?',
                       (one_word, ))
        amount_rep = []
        amount_rep.append(cursor.fetchone())
        amount_rep = [i[0] for i in amount_rep]
        next_rep = amount_rep[0] + 2
        data_next_rep = current_date + datetime.timedelta(days=next_rep)
        cursor.execute(
            f'UPDATE {idn} SET data_next_rep = ?, amount_of_rep =+ 1 WHERE new_words = ?',
            (
                data_next_rep.strftime("%d/%m/%Y"),
                one_word,
            ))
        conn.commit()
        amount_rep[0] += 1
        if amount_rep[0] == 7:
            cursor.execute(
                f'UPDATE {idn} SET data_next_rep = NULL, complete_words = 1 WHERE new_words = {one_word}'
            )
            bot.send_message(chat_id, '🎉Вітаю, ти вивчив це слово 🥳🥇')
            conn.commit()
        foo(callback.message)
    elif callback.data == 'false':
        bot.send_message(
            chat_id,
            'Що ж, чим більше ти помиляєшся, тим кращим буде кінцевий результат.'
        )
        worder.insert(len(worder) - 1, one_word)
        #Додати цілі слова, аби потім додати функцію перегляду, які слова згадав, а які ні
        if one_word not in stat_false:
            stat_false.append(one_word)
        foo(info_user)
    elif callback.data == 'tru':
        bot.send_message(chat_id, 'Молодець! Це слово було повторено❤️')
        foos(info_user)
    elif callback.data == 'fals':
        bot.send_message(
            chat_id,
            'Що ж, чим більше ти помиляєшся, тим кращим буде кінцевий результат.'
        )
        worder.insert(len(worder) - 1, one_word)
        if one_word not in stat_false:
            stat_false.append(one_word)
        foos(info_user)
    elif callback.data == 'data':
        daily_photo(info_user)
    elif callback.data == 'repeat':
        repeat(info_user)
    elif callback.data == 'teach':
        teach(info_user)
    elif callback.data in numbers:
        repeat_data(info_user, callback.data)
    elif callback.data == 'english':
        english_form(info_user)
    elif callback.data == 'words':
        words(info_user)
    elif callback.data == 'learn':
        new_words(info_user)
    elif callback.data == 'added_today':
        show_words(info_user)


# НАПИСАТИ СЛОВА, ЯКІ ТИ ВИВЧИВ
@bot.callback_query_handler(func=lambda callback: callback.data == 'completo')
def callback_insert(callback):
    bot.send_message(chat_id, 'Введіть вивчене слово: ')
    bot.register_next_step_handler(callback.message, iii)


def iii(message):
    if message.text == 'end':
        show_words(message)
    else:
        insert(message)
        cursor.execute(
            f'SELECT complete_words FROM {idn} WHERE complete_words = ?',
            (message.text, ))
        existing_word = cursor.fetchone()

        if existing_word:
            bot.send_message(chat_id,
                             f'Слово "{message.text}" вже є в базі даних.')
        else:
            cursor.execute(
                f'INSERT INTO {idn} (complete_words, data_new_words) VALUES (?, ?)',
                (message.text, ))
            conn.commit()
        bot.send_message(chat_id, 'Слово успішно збережено')
        bot.send_message(chat_id, 'Введіть вивчене слово: ')
        bot.register_next_step_handler(message, iii)


# callback для кнопок в repeat()
def repeat_data(message, data):
    keyboard = types.InlineKeyboardMarkup()
    named = ['Programing', 'English', 'Mental']
    for i in range(3):
        keyboard.add(
            types.InlineKeyboardButton(named[i],
                                       callback_data=named[i].lower()))
    bot.send_message(chat_id,
                     f'Вибери тему за <b>{str(data)}.10</b>: ',
                     reply_markup=keyboard,
                     parse_mode='html')


@bot.message_handler(commands=['info'])
def info(message):
    id_user(message)
    bot.send_message(chat_id, '///Функція в розробці///')


@bot.message_handler(commands=['future'])
def future(message):
    id_user(message)
    bot.send_message(
        chat_id,
        '1. Повідомлення-нагадування про навчання.\n2. Можливість відкладати нагадування.\n3. touch для слів, які можна окремо вибрати.\n4. Можливість створення власних цілей.\n5. Можливість видалення слів з навчання.\n6. Оновлення інтерфейсу (Замість нового повідомлення, буде замінювати попереднє.'
    )


bot.infinity_polling()
