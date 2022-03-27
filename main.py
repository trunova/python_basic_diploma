import telebot
from telebot import types
import requests
import json
from lowprice import Lowprice
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
value: str = '0'

myLowprice: Lowprice = Lowprice(bot)

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


@bot.message_handler(commands=['start', 'hello-world'])
def welcome(message: types.Message):
    bot.send_message(message.from_user.id,
                     "Привет, {name1}, меня зовут @TooEasyTravelBot.\n"
                     "Я бот турагентства Too Easy Travel, "
                     "который поможет Вам подобрать подходящий отель для проживания.\n"
                     "Вы можете управлять мной, отправив следующие команды:\n"
                     "/help — помощь по командам бота\n"
                     "/lowprice - вывод самых дешёвых отелей в городе\n"
                     "/highprice - вывод самых дорогих отелей в городе\n"
                     "/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n"
                     "/history - вывод истории поиска отелей\n".format(name1=message.from_user.first_name),
                     reply_markup=None)


@bot.message_handler(commands=['help'])
def help(message: types.Message):
    bot.send_message(message.chat.id,
                     "Вы можете управлять мной, отправив следующие команды:\n"
                     "/help — помощь по командам бота\n"
                     "/lowprice - вывод самых дешёвых отелей в городе\n"
                     "/highprice - вывод самых дорогих отелей в городе\n"
                     "/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n"
                     "/history - вывод истории поиска отелей\n")


@bot.message_handler(commands=['lowprice'])
def users_sity(message: types.Message):
    myLowprice.zeroingValues()
    sent = bot.send_message(message.chat.id, "Укажите город, где будет проводиться поиск")
    bot.register_next_step_handler(sent, count_hotels)

def count_hotels(message: types.Message):
    myLowprice.sity = message.text
    bot.send_message(message.chat.id, "Укажите количество отелей, "
                                      "которые необходимо вывести (не больше 15)")
    bot.send_message(message.chat.id, "0", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global value
    try:
        if call.message:
            if call.data == 'yes':
                help(call.message)
            elif call.data == 'no':
                bot.send_message(call.message.chat.id, "Чем тогда я могу помочь?")
                bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Привет, тебе нужна помощь с подбором отеля?",
                                  reply_markup=None)
            elif call.data == 'yesPhoto':
                myLowprice.uploadPhoto = True
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Необходимо загружать фотографий для каждого отеля?",
                                      reply_markup=None)
                bot.send_message(call.message.chat.id, "Введите количество необходимых фотографий (не больше 5)",
                                        reply_markup=None)
                bot.send_message(call.message.chat.id, "0", reply_markup=keyboard)
            elif call.data == 'noPhoto':
                myLowprice.uploadPhoto = False
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Необходимо загружать фотографий для каждого отеля?",
                                      reply_markup=None)
                myLowprice.lowprice(call.message)
            elif call.data in '0123456789':
                if value == '0':
                    value = call.data
                else: value += call.data
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=value,
                                      reply_markup=keyboard)
            elif call.data == '<=':
                if len(value) <= 1: value = '0'
                else:
                    value = value[0: len(value)-1]
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=value,
                                      reply_markup=keyboard)
            elif call.data == 'ok':
                if int(value) > 15: value = '15'
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=value,
                                      reply_markup=None)
                if myLowprice.count(int(value), call.message):
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    item1 = types.InlineKeyboardButton("Да", callback_data='yesPhoto')
                    item2 = types.InlineKeyboardButton("Нет", callback_data='noPhoto')
                    markup.add(item1, item2)
                    bot.send_message(call.message.chat.id, "Необходимо загружать фотографий для каждого отеля?",
                                     reply_markup=markup)
                value = '0'
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
