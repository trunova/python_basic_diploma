import telebot
from telebot import types

bot = telebot.TeleBot('5191120420:AAHpcFUbmSBNgokxO1Ny4EEiQo9vvNsaguU')

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

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
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
