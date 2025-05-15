import sqlite3

import requests
import telebot
import webbrowser
from telebot import types
from telebot.types import InlineKeyboardButton
from currency_converter import CurrencyConverter
import json

bot = telebot.TeleBot('7791067670:AAGcRhDVSdgSWdb_RdkKfjqhbjqjKSr1S8o')
currency = CurrencyConverter()
apikey = 'eabc22da15103f4edf6b2b9d7fd60afd'

name = ''
amount = 0
i = 0
flag = True
flag_weather = False


@bot.message_handler(commands=['weather'])
def local_weather(message):
    global flag_weather
    flag_weather = True
    bot.send_message(message.chat.id, 'Хорошей погоды! Напиши название города')
    requests.get('https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={}')


# Обработка фото
@bot.message_handler(content_types=['photo'])
def photo(message):
    markup = types.InlineKeyboardMarkup()

    site_button = types.InlineKeyboardButton('Перейти на сайт',
                                             url='https://www.okx.com/ru-eu/price/bitcoin-btc')
    delete_button = InlineKeyboardButton('Удалить фото', callback_data='delete')
    change_button = types.InlineKeyboardButton('Изменить текст', callback_data='edit')

    # Стилизуем кнопки
    markup.row(site_button)
    markup.row(delete_button, change_button)

    bot.reply_to(message, 'Какое красивое фото!', reply_markup=markup)


@bot.message_handler(commands=['currency'])
def money(message):
    bot.send_message(message.chat.id, 'Привет, введите сумму')
    bot.register_next_step_handler(message, summa)


def summa(message):
    global amount
    # Проверка на строки и отрицательные числа
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат, введите сумму')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
        return
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше 0, введите сумму')
        bot.register_next_step_handler(message, summa)
        return


@bot.message_handler(commands=['site', 'website'])
def open_site(message):
    webbrowser.open('https://openexchangerates.org')


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                    f'Привет, {message.from_user.first_name}. '
                    f'Чтобы узнать как я работаю введи <b>/help</b>',
                    parse_mode='html'
                     )
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'Перейти на сайт':
        webbrowser.open('https://openexchangerates.org')


# Потом дописать все команды
@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}\n'
                     f'Бот умеет конвертировать валюты, обрабатывать фотографии, узнавать текущую погоду в твоём городе.\n'
                     '/help - Помощь в использовании бота\n'
                     '/site - Сайт с валютами\n'
                     '/website - Сайт с валютами\n'
                     '/currency - Конвертер валют\n'
                     '/register - Зарегистрировать пользователя\n'
                     '/elephant - "Купи слона"\n'
                     '/start - Запуск программы\n'
                     '/rest - Смайлик с котом\n'
                     '/id - Узнать ID пользователя\n'
                     '/weather - Узнать погоду\n')


#     Хранение в БД
@bot.message_handler(commands=['register'])
def register(message):
    conn = sqlite3.connect('traderbot.sql')
    cur = conn.cursor()

    query = 'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))'
    cur.execute(query)
    conn.commit()

    # закрывам соеденение
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет! Щас тебя зарегистрируем, введи своё имя')
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('traderbot.sql')
    cur = conn.cursor()

    query = f'INSERT INTO users (name, pass) VALUES ("%s", "%s")' % (name, password)
    cur.execute(query)
    conn.commit()

    # закрывам соеденение
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'users':
        conn = sqlite3.connect('traderbot.sql')
        cur = conn.cursor()

        query = f'SELECT * FROM users'
        cur.execute(query)

        users = cur.fetchall()

        info = ''
        for elem in users:
            info += f'Имя: {elem[1]}, пароль: {elem[2]}\n'

        #  Закрывам соеденение

        cur.close()
        conn.close()

        bot.send_message(call.message.chat.id, info)

    # Обработка фото

    elif call.data == 'delete':
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    elif call.data == 'edit':
        bot.edit_message_text('Поздравляю! Ты изменил текст.',
                              call.message.chat.id,
                              call.message.message_id)
    #     Конвертер валют

    if call.data == 'usd/eur' or call.data == 'eur/usd' or call.data == 'usd/gbp':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Получаестя {round(res, 2)}')
    elif call.data == 'else':
        bot.send_message(call.message.chat.id, 'Введите пару значений через слэш')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Получаестя {round(res, 2)}')
        return
    except Exception:
        bot.send_message(message.chat.id, 'Что-то не так. Введите значение заново')
        bot.register_next_step_handler(message, my_currency)


@bot.message_handler(commands=['elephant'])
def elephant_game(message):
    global i
    global flag
    if flag:
        bot.send_message(message.chat.id, 'Купи слона')
        flag = False
    if i > 0:
        if message.text.lower() == 'купить слона':
            webbrowser.open(
                url='https://www.ozon.ru/category/myagkie-igrushki-slon/?__rr=1&abt_att=1&origin_referer=yandex.ru')
            i = 0
            return
        else:
            bot.send_message(message.chat.id, f'Все говорят, {message.text}, а ты купи слона')
    i += 1
    bot.register_next_step_handler(message, elephant_game)


@bot.message_handler(commands=['id'])
def identifier(message):
    bot.reply_to(message, f'ID: {message.from_user.id}')


@bot.message_handler(content_types=['text'])
def info(message):
    global flag_weather
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
        return
    if message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')
        return
    if flag_weather:
        city = message.text.strip().lower()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&units=metric')
        if res.status_code == 200:
            data = json.loads(res.text)
            temp = data['main']['temp']
            bot.reply_to(message, f'Сейчас погода: {temp}')

            image = 'sunny.png' if temp > 5.0 else 'rainy.jpg'
            file = open('./' + image, 'rb')
            bot.send_photo(message.chat.id, file)
        else:
            bot.reply_to(message, 'Город указан неверно ')
        flag_weather = False
        return


bot.infinity_polling()
