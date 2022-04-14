import copy
import re
import sys
import datetime
import telegramcalendar
import telebot
from telebot import types
import requests
import json
from hotel_search_engine import Hotel_search_engine
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
value: str = '0'

search_engine: Hotel_search_engine = Hotel_search_engine(bot)

keyboard = types.InlineKeyboardMarkup()
keyboard.row(types.InlineKeyboardButton('7', callback_data= '7'),
             types.InlineKeyboardButton('8', callback_data= '8'),
             types.InlineKeyboardButton('9', callback_data= '9')
             )
keyboard.row(types.InlineKeyboardButton('4', callback_data= '4'),
             types.InlineKeyboardButton('5', callback_data= '5'),
             types.InlineKeyboardButton('6', callback_data= '6')
             )
keyboard.row(types.InlineKeyboardButton('1', callback_data= '1'),
             types.InlineKeyboardButton('2', callback_data= '2'),
             types.InlineKeyboardButton('3', callback_data= '3')
             )
keyboard.row(types.InlineKeyboardButton('0', callback_data= '0'),
             types.InlineKeyboardButton('отмена', callback_data= '<='),
             types.InlineKeyboardButton('ок', callback_data='ok')
            )

keyboard_price = types.InlineKeyboardMarkup()
keyboard_price.row(types.InlineKeyboardButton('<--', callback_data='<--'),
                   types.InlineKeyboardButton('-->', callback_data='-->'),
                   types.InlineKeyboardButton('ok', callback_data='ok')
                   )
keyboard_price.row(types.InlineKeyboardButton('изменить валюту', callback_data='change_currency'))
keyboard_price.row(types.InlineKeyboardButton('ввести самостоятельно', callback_data='enter_yourself'))

keyboard_enter_yourself = types.InlineKeyboardMarkup()
keyboard_enter_yourself.row(types.InlineKeyboardButton('7', callback_data='7'),
         types.InlineKeyboardButton('8', callback_data='8'),
         types.InlineKeyboardButton('9', callback_data='9')
         )
keyboard_enter_yourself.row(types.InlineKeyboardButton('4', callback_data='4'),
         types.InlineKeyboardButton('5', callback_data='5'),
         types.InlineKeyboardButton('6', callback_data='6')
         )
keyboard_enter_yourself.row(types.InlineKeyboardButton('1', callback_data='1'),
         types.InlineKeyboardButton('2', callback_data='2'),
         types.InlineKeyboardButton('3', callback_data='3')
         )
keyboard_enter_yourself.row(types.InlineKeyboardButton('USD', callback_data='USD2'),
                  types.InlineKeyboardButton('EUR', callback_data='EUR2'),
                  types.InlineKeyboardButton('GBP', callback_data='GBP2')
                  )
keyboard_enter_yourself.row(types.InlineKeyboardButton('JPY', callback_data='JPY2'),
                  types.InlineKeyboardButton('CHF', callback_data='CHF2'),
                  types.InlineKeyboardButton('CNY', callback_data='CNY2'),
                  types.InlineKeyboardButton('RUB', callback_data='RUB2')
                  )
keyboard_enter_yourself.row(types.InlineKeyboardButton('0', callback_data='0'),
         types.InlineKeyboardButton('отмена', callback_data='<='),
         types.InlineKeyboardButton('ок', callback_data='ok')
         )

keyboard_distance = types.InlineKeyboardMarkup()
keyboard_distance.row(types.InlineKeyboardButton('7', callback_data= '7'),
             types.InlineKeyboardButton('8', callback_data= '8'),
             types.InlineKeyboardButton('9', callback_data= '9')
             )
keyboard_distance.row(types.InlineKeyboardButton('4', callback_data= '4'),
             types.InlineKeyboardButton('5', callback_data= '5'),
             types.InlineKeyboardButton('6', callback_data= '6')
             )
keyboard_distance.row(types.InlineKeyboardButton('1', callback_data= '1'),
             types.InlineKeyboardButton('2', callback_data= '2'),
             types.InlineKeyboardButton('3', callback_data= '3')
             )
keyboard_distance.row(types.InlineKeyboardButton('m', callback_data= ' m'),
             types.InlineKeyboardButton('km', callback_data= 'km'),
             types.InlineKeyboardButton('ок', callback_data='ok')
            )
keyboard_distance.row(types.InlineKeyboardButton('0', callback_data= '0'),
             types.InlineKeyboardButton('отмена', callback_data= '<='),
            )

@bot.message_handler(commands=['start', 'hello-world'])
def welcome(message: types.Message):
    bot.send_message(message.from_user.id,
                     "Привет, {name1}, меня зовут @TooEasyTravelBot.\n"
                     "Я бот турагентства Too Easy Travel, "
                     "который поможет Вам подобрать подходящий отель для проживания.\n"
                     "Вы можете управлять мной, отправив следующие команды:\n"
                     "/help - помощь по командам бота\n"
                     "/select_dates - выбор сроков проживания в отеле (по умолчанию установится текущая дата и срок проживания 10 дней)\n"
                     "/lowprice - вывод самых дешёвых отелей в городе\n"
                     "/highprice - вывод самых дорогих отелей в городе\n"
                     "/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n"
                     "/history - вывод истории поиска отелей\n".format(name1=message.from_user.first_name),
                     reply_markup=None)


@bot.message_handler(commands=['help'])
def help(message: types.Message):
    bot.send_message(message.chat.id,
                     "Вы можете управлять мной, отправляя следующие команды:\n"
                     "/help - помощь по командам бота\n"
                     "/select_dates - выбор сроков проживания в отеле (по умолчанию установится текущая дата и срок проживания 10 дней)\n"
                     "/lowprice - вывод самых дешёвых отелей в городе\n"
                     "/highprice - вывод самых дорогих отелей в городе\n"
                     "/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n"
                     "/history - вывод истории поиска отелей\n")


@bot.message_handler(commands=['history'])
def history(message: types.Message):
    history_text = ''
    with open('history.txt', 'r') as file:
        text = file.read().split('\n')
        for line in text:
            lst = line.split('|')
            if lst == ['']: break
            history_text += "Команда: {command};\nДата ввода: {date};\nВремя ввода: {time}\n" \
                            "Список отелей: {list_hotels}\n\n".format(command=lst[0],
                                                                     date=lst[1],
                                                                     time=lst[2],
                                                                     list_hotels=lst[3:])
    bot.send_message(message.chat.id, history_text)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def users_sity(message: types.Message):
    with open('history.txt', 'a') as file:
        file.write(message.text + '|')
        file.write(str(datetime.datetime.now().date()) + '|')
        file.write(str(datetime.datetime.now().time()) + '|')

    search_engine.zeroingValues()
    if message.text == '/highprice':
        search_engine.sort_order = 'PRICE_HIGHEST_FIRST'
    sent = bot.send_message(message.chat.id, "Укажите город, где будет проводиться поиск")
    if message.text == '/bestdeal':
        bot.register_next_step_handler(sent, price_range)
        return
    bot.register_next_step_handler(sent, count_hotels)


def price_range(message: types.Message):
    """ Функция, запрашивающая диапазон цен """
    search_engine.sity = message.text
    bot.send_message(message.chat.id, "Укажите необходимый диапазон цен")

    bot.send_message(message.chat.id, "Минимальная цена: 0 USD", reply_markup=keyboard_price)
    bot.send_message(message.chat.id, "Максимальная цена: 0 USD", reply_markup=keyboard_price)


def count_hotels(message: types.Message):
    search_engine.sity = message.text
    bot.send_message(message.chat.id, "Укажите количество отелей, "
                                      "которые необходимо вывести (не больше 15)")
    bot.send_message(message.chat.id, "0", reply_markup=keyboard)


@bot.message_handler(commands=['select_dates'])
def arrival_date(message: types.Message):
    bot.send_message(message.chat.id, "Укажите дату заселения в отель: ", reply_markup=telegramcalendar.create_calendar())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global value
    try:
        if call.message:
            if call.data == 'yes':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text,
                                      reply_markup=None)
                help(call.message)
            elif call.data == 'no':
                bot.send_message(call.message.chat.id, "Чем тогда я могу помочь?")
                bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=call.message.text,
                                  reply_markup=None)
            elif call.data == 'yesPhoto':
                search_engine.uploadPhoto = True
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text,
                                      reply_markup=None)
                bot.send_message(call.message.chat.id, "Введите количество необходимых фотографий (не больше 5)",
                                        reply_markup=None)
                bot.send_message(call.message.chat.id, "0", reply_markup=keyboard)
            elif call.data == 'noPhoto':
                search_engine.uploadPhoto = False
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text,
                                      reply_markup=None)
                search_engine.lowprice(call.message)
            elif call.data in '0123456789':
                if value == '0':
                    value = call.data
                else: value += call.data
                if 'цена:' in call.message.text:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=re.sub(r'\d+', value, call.message.text),
                                      reply_markup=keyboard_enter_yourself)
                elif 'расстояние' in call.message.text:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          text=re.sub(r'\d+', value, call.message.text),
                                          reply_markup=keyboard_distance)
                else: bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=re.sub(r'\d+', value, call.message.text),
                                      reply_markup=keyboard)
            elif call.data == '<=':
                if len(value) <= 1: value = '0'
                else:
                    value = value[0: len(value)-1]
                if 'цена:' in call.message.text:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=re.sub(r'\d+', value, call.message.text),
                                      reply_markup=keyboard_enter_yourself)
                elif 'расстояние' in call.message.text:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          text=re.sub(r'\d+', value, call.message.text),
                                          reply_markup=keyboard_distance)
                else: bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=re.sub(r'\d+', value, call.message.text),
                                      reply_markup=keyboard)
            elif call.data == 'ok':
                mess = call.message.text
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=mess,
                                      reply_markup=None)
                if 'цена:' in mess:
                    search_engine.currency = mess[len(mess) - 3:]
                    if 'Максимальная' in mess:
                        search_engine.max_price = int(value)
                        bot.send_message(call.message.chat.id, "Укажите минимальное расстояние, "
                                                               "на котором должен находиться отель от центра:\n0 m",
                                         reply_markup=keyboard_distance)
                    else:
                        search_engine.min_price = int(value)
                elif 'расстояние' in mess:
                    if 'минимальное' in mess:
                        if not 'km' in mess: value = int(value) / 1000
                        search_engine.min_distance = float(value)
                        search_engine.sort_order += '|DISTANCE_FROM_LANDMARK'
                        bot.send_message(call.message.chat.id, "Укажите максимальное расстояние, "
                                                               "на котором должен находиться отель от центра:\n0 km",
                                         reply_markup=keyboard_distance)
                    else:
                        if not 'km' in mess: value = int(value) / 1000
                        search_engine.max_distance = float(value)
                        bot.send_message(call.message.chat.id, "Укажите количество отелей, "
                                                               "которые необходимо вывести (не больше 15)")
                        bot.send_message(call.message.chat.id, "0", reply_markup=keyboard)

                elif search_engine.count(int(value), call.message):
                    if int(value) > 15: value = '15'
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item1 = types.InlineKeyboardButton("Да", callback_data='yesPhoto')
                    item2 = types.InlineKeyboardButton("Нет", callback_data='noPhoto')
                    markup.add(item1, item2)
                    bot.send_message(call.message.chat.id, "Необходимо загружать фотографий для каждого отеля?",
                                     reply_markup=markup)
                value = '0'
            elif call.data == '-->':
                value = str(int(value) + 1000)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text='{name_price}: {price} USD'.format(
                                          name_price= call.message.text[: call.message.text.index(':')],
                                          price=value),
                                      reply_markup=keyboard_price)
            elif call.data == '<--':
                value = str(int(value) + 1000)
                if value < 0: value = 0
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text='{name_price}: {price} USD'.format(
                                          name_price=call.message.text[: call.message.text.index(':')],
                                          price=value),
                                      reply_markup=keyboard_price)
            elif call.data == 'change_currency':
                keyboard_currency = types.InlineKeyboardMarkup()
                keyboard_currency.row(types.InlineKeyboardButton('USD', callback_data='USD'),
                             types.InlineKeyboardButton('EUR', callback_data='EUR'),
                             types.InlineKeyboardButton('GBP', callback_data='GBP')
                             )
                keyboard_currency.row(types.InlineKeyboardButton('JPY', callback_data='JPY'),
                                      types.InlineKeyboardButton('CHF', callback_data='CHF'),
                                      types.InlineKeyboardButton('CNY', callback_data='CNY'),
                                      types.InlineKeyboardButton('RUB', callback_data='RUB')
                                      )
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text,
                                      reply_markup=keyboard_currency)
            elif call.data == 'enter_yourself':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text,
                                      reply_markup=keyboard_enter_yourself)
            elif call.data in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CNY', 'RUB']:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text[: len(call.message.text) - 3] + call.data,
                                      reply_markup=keyboard_price)
            elif call.data in ['USD2', 'EUR2', 'GBP2', 'JPY2', 'CHF2', 'CNY2', 'RUB2']:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text[: len(call.message.text) - 3] + call.data[:3],
                                      reply_markup=keyboard_enter_yourself)
            elif call.data in [' m', 'km']:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=call.message.text[: len(call.message.text) - 2] + call.data[:2],
                                      reply_markup=keyboard_distance)
            else:
                date = telegramcalendar.process_calendar_selection(bot, call)[1]
                if date != None:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          text="Дата {t} {d}".format(t=call.message.text[13:], d=date.date()),
                                          reply_markup=None)
                    if "заселения" in call.message.text:
                        search_engine.arrival_date = date
                        bot.send_message(call.message.chat.id, "Укажите дату выезда из отеля: ",
                                         reply_markup=telegramcalendar.create_calendar())
                    elif "выезда" in call.message.text:
                        search_engine.departure_date = date
                        if search_engine.correct_dates():
                            bot.send_message(call.message.chat.id, "Сроки проживания в отеле установлены корректно (/help)")
                        else:
                            bot.send_message(call.message.chat.id, "Сроки проживания в отеле указаны некорректно, "
                                                                   "повторите попытку (/select_dates)")
    except Exception as e:
        print(repr(e))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: types.Message):
    if message.chat.type == 'private':
        if message.text.lower() == "привет":
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data='yes')
            item2 = types.InlineKeyboardButton("Нет", callback_data='no')

            markup.add(item1, item2)
            bot.send_message(message.from_user.id, "Привет, тебе нужна помощь с подбором отеля?", reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
