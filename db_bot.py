import telebot
import sqlite3
from threading import Lock
from telebot import types

bot = telebot.TeleBot('...') # you token


db_lock = Lock()


@bot.message_handler(func=lambda message: message.text.lower() == '/start')
def start_message(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/Problems')
    btn2 = types.KeyboardButton('/Help')
    btn3 = types.KeyboardButton('/My problems')

    markup.row(btn1)
    markup.row(btn2, btn3)

    bot.send_message(message.chat.id, f"Привіт, {message.from_user.first_name}, давай розпочнемо роботу, "
                                      f"натисніть 'help', дяя детальної інформації", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.lower() == '/help')
def help_message(message):
    bot.send_message(message.chat.id,
                     "Цей бот створений для передачі проблем готелю (назва готелю) на сайт (назва сайту)."
                     " Якщо у вас є проблема, про яку треба повідомити, натисніть на кнопку 'problem' та введіть дані."
                     "Щоб подивитись проблеми, які ви вже ввели, натисніть на кнопку 'My problems' ")


@bot.message_handler(func=lambda message: message.text.lower() == '/problems')
def problem_handler(message):
    bot.send_message(message.chat.id, "Введіть номер квартири:")
    bot.register_next_step_handler(message, get_apartment_number)


def get_apartment_number(message):
    apartment_number = message.text
    bot.send_message(message.chat.id, "Введіть текст проблеми:")
    bot.register_next_step_handler(message, save_problem, apartment_number)


def save_problem(message, apartment_number):
    error_number = message.text
    bot.send_message(message.chat.id,
                     f"{apartment_number}, {error_number} \nВаша проблема успішно внесена до бази даних")

    with db_lock:
        db = sqlite3.connect('problems.db', check_same_thread=False)
        cursor = db.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problem (
                apartment_number INTEGER,
                problem_text TEXT
            )
        ''')
        db.commit()

        insert_cursor = db.cursor()
        insert_cursor.execute("INSERT INTO problem VALUES (?, ?)", (apartment_number, error_number))
        db.commit()

        insert_cursor.close()

        db.close()

    @bot.message_handler(func=lambda message: message.text.lower() == '/my problems')
    def problem_handler(message):
        with db_lock:
            db = sqlite3.connect('problems.db', check_same_thread=False)
            cursor = db.cursor()

            for value in cursor.execute("SELECT * FROM problem"):
                bot.send_message(message.chat.id, f"{value}")

            db.close()


if __name__ == "__main__":
    bot.infinity_polling()
