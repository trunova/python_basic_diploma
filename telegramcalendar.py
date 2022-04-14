import datetime
import calendar
from telebot import types

def create_calendar(year=None,month=None):
    """ Создание календаря в виде types.InlineKeyboardMarkup """
    now = datetime.datetime.now()
    if year == None: year = now.year
    if month == None: month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    keyboard.append([types.InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data=data_ignore)])
    row=[]
    for day in ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]:
        row.append(types.InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if (day == 0):
                row.append(types.InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(
                    types.InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.append(row)
    row = []
    row.append(types.InlineKeyboardButton("<--", callback_data=create_callback_data("PREV-MONTH", year, month, day)))
    row.append(types.InlineKeyboardButton(" ", callback_data=data_ignore))
    row.append(types.InlineKeyboardButton("-->", callback_data=create_callback_data("NEXT-MONTH", year, month, day)))
    keyboard.append(row)
    return types.InlineKeyboardMarkup(keyboard)



def create_callback_data(action, year, month, day):
    return ";".join([action, str(year), str(month), str(day)])


def process_calendar_selection(bot, call) -> tuple:
    """ Обработка основных действий по нажатию на кнопки календаря """
    ret_data = (False,None)
    (action,year,month,day) = call.data.split(';')
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id= call.id)
    elif action == "DAY":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=call.message.text
            )
        ret_data = True,datetime.datetime(int(year),int(month),int(day))
    elif action == "PREV-MONTH":
        prev = curr - datetime.timedelta(days=1)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=call.message.text,
            reply_markup=create_calendar(int(prev.year),int(prev.month)))
    elif action == "NEXT-MONTH":
        next = curr + datetime.timedelta(days=31)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=call.message.text,
                                reply_markup=create_calendar(int(next.year),int(next.month)))
    return ret_data