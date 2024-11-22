from datetime import datetime as dt
from datetime import timedelta
import sqlite3


def insert(message):
  global conn, cursor, idn
  idn = 'Kiryllchik'
  conn = sqlite3.connect('base.bd')
  cursor = conn.cursor()
  cursor.execute(f'''CREATE TABLE IF NOT EXISTS {idn} 
                 (new_words TEXT, 
                 data_new_words DATA, 
                 data_next_rep DATA, 
                 amount_of_rep INTEGER, 
                 complete_words TEXT)''')
  conn.commit()


  
def curr_date():
  global current_date
  current_date = dt.now()

def teach(message):
    insert(message)
    current_date = dt.now()
    one_word = 'Polite'
    cursor.execute(f'SELECT amount_of_rep FROM {idn} WHERE new_words = ?', (one_word,))
    amount_rep = []
    amount_rep.append(cursor.fetchone())
    amount_rep = [i[0] for i in amount_rep]
    print(amount_rep[0]+2)
    data_next_rep = current_date + timedelta(days=amount_rep[0]+2)
    print(data_next_rep.strftime("%d/%m/%Y"))
    
    cursor.execute(f'UPDATE {idn} SET data_next_rep = ?, amount_of_rep =+ 1 WHERE new_words = ?', (data_next_rep.strftime("%d/%m/%Y"), one_word,))
    conn.commit()
    """for i in words.values():
        date_object = dt.strptime(i, "%d/%m/%Y")
        data.append(date_object)
    print(data)"""
teach('message')


'words'
'learn'
'added_today'