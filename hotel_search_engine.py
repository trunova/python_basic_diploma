import sys
import datetime
import requests
import re
import time
import json
import telebot
from telebot import types


class Hotel_search_engine:
    """
    Класс, хранящий данные для поиска отелей в указанном городе городе по различным характеристикам

    Args:
        bot(telebot.TeleBot): передаётся бот
    """

    def __init__(self, bot):
        self._bot = bot
        self._sity = ''
        self._countHotels = 0
        self._uploadPhoto = False
        self._countPhoto = 0
        self._sort_order = "PRICE"
        self._min_price = 0
        self._max_price = sys.float_info.max
        self._min_distance = 0
        self._max_distance = sys.float_info.max
        self._currency = 'USD'
        self._arrival_date = datetime.datetime.now()
        self._departure_date = self._arrival_date + datetime.timedelta(days=10)


    def zeroingValues(self):
        """ Функция для обнуления всех параметров класса """
        self._sity = ' '
        self._countHotels = 0
        self._uploadPhoto = False
        self._countPhoto = 0
        self._sort_order = "PRICE"
        self._min_price = 0
        self._max_price = sys.float_info.max
        self._min_distance = 0
        self._max_distance = sys.float_info.max
        self._currency = 'USD'


    def count(self, count: int, message: types.Message) -> bool:
        """
        Функция, устанавливающая количество отелей, и запускающая их поиск

        :param count: количество отелей
        :param message: сообщение
        :rtype: bool
        """
        if self._countHotels == 0:
            if count > 15: count = 15
            self.countHotels = count
            return True
        elif self._countPhoto == 0 and self._uploadPhoto:
            if count > 10: count = 10
            self.countPhoto = count
            self.lowprice(message)
            return False
        return False


    def correct_dates(self) -> bool:
        """ Функция, проверяющая корректность введённых дат"""
        if self._arrival_date < self._departure_date:
            return True
        else:
            self._arrival_date = datetime.datetime.now()
            self._departure_date = self._arrival_date + datetime.timedelta(days=10)
            return False


    def lowprice(self, message: types.Message):
        """
        Функция, производящая поиск отелей по заданным параметрам

        :param message: сообщение
        """

        self._bot.send_message(message.chat.id, "Идёт поиск подходящих отелей..")
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": self._sity.lower(), "locale": "en_US", "currency": "USD"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "7d50f060demshbf403a76fd0f28ap136b16jsne3ca74cf90e8"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)

        destinationId = data.get("suggestions")[0].get("entities")[0].get("destinationId")
        lat_centre = data.get("suggestions")[0].get("entities")[0].get("latitude")
        lon_centre = data.get("suggestions")[0].get("entities")[0].get("longitude")

        url_city = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": 25,
                       "checkIn": str(self._arrival_date.date()), "checkOut": str(self._departure_date.date()),
                       "adults1": "1", "priceMin": str(self._min_price), "priceMax": str(self._max_price),
                       "sortOrder": self._sort_order, "locale": "en_US",
                       "currency": self._currency, "accommodationIds":"1, 3"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "7d50f060demshbf403a76fd0f28ap136b16jsne3ca74cf90e8"
        }
        response2 = requests.request("GET", url_city, headers=headers, params=querystring)
        data_hotels = json.loads(response2.text)
        count_days = int(self._departure_date.day) - int(self._arrival_date.day)
        new_count_hotels = 0
        with open('history.txt', 'a') as file:
            for i_hotel in data_hotels.get("data").get("body").get("searchResults").get("results"):
                if new_count_hotels >= self._countHotels: break
                distance = float(i_hotel['landmarks'][0]['distance'][:i_hotel['landmarks'][0]['distance'].index(' ')])
                if distance > self._max_distance: break
                if distance > self._min_distance:
                    new_count_hotels += 1
                    hotel_id = i_hotel.get("id")
                    price = i_hotel.get("ratePlan").get("price").get("current")
                    if ',' in price:
                        all_price_int = int(re.search(r'\d+,', price).group(0)[:-1] +
                                   re.search(r',\d+', price).group(0)[1:]) * count_days
                        all_price = re.sub(r'\d+,\d+', str(all_price_int), price)
                    else:
                        all_price = re.sub(r'\d+', str(int(re.search(r'\d+', price).group(0)) * count_days), price)

                    self._bot.send_message(message.chat.id, "Отель №{i}:\nНазвание: \"{name}\"\nАдрес: {address}\n"
                                                            "Расположение относительно центра: "
                                                            "{location} km\nЦена: {price}\n"
                                                            "Суммарная стоимость за указанный период: {all_price}\n"
                                                            "https://ru.hotels.com/ho{id}".format(
                        i=new_count_hotels,
                        name=i_hotel.get("name"),
                        address=i_hotel.get("address").get("streetAddress"),
                        location=str(distance),
                        price=price,
                        all_price=all_price,
                        id=hotel_id))
                    file.write(i_hotel.get("name") + '|')
                    if self._uploadPhoto:
                        url_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                        querystring_photo = {"id": hotel_id}
                        headers_photo = {
                            'x-rapidapi-host': "hotels4.p.rapidapi.com",
                            'x-rapidapi-key': "7d50f060demshbf403a76fd0f28ap136b16jsne3ca74cf90e8"
                        }

                        response_photo = requests.request("GET", url_photo, headers=headers_photo, params=querystring_photo)
                        data_photo = json.loads(response_photo.text)

                        for i in range(self.countPhoto):
                            img_url = data_photo.get("hotelImages")[i].get("baseUrl").format(size='b')
                            requests.get(f'https://api.telegram.org/bot{self._bot.token}/sendPhoto?chat_id={message.chat.id}&photo={img_url}')
            else: self._bot.send_message(message.chat.id, 'Подходящих отелей не нашлось, попробуйте выбрать другие параметры поиска (/help)')
            file.write('\n')


    @property
    def sity(self) -> str:
        """
        Геттер для получения города

        :return: __sity
        :rtype: str
        """
        return self._sity

    @sity.setter
    def sity(self, sity:str):
        """
        Сеттер для установления города

        :param sity: город
        """
        self._sity = sity

    @property
    def countHotels(self) -> int:
        """
        Геттер для получения количества отелей

        :return: __countHotels
        """
        return self._countHotels

    @countHotels.setter
    def countHotels(self, countHotels: int):
        """
        Сеттер для установления количества отелей

        :param countHotels: количество отелей
        """
        self._countHotels = countHotels

    @property
    def uploadPhoto(self) -> bool:
        """
        Геттер для получения флага, отвечающего за прикрепление фотографий к отелю

        :return: __uploadPhoto
        """
        return self._uploadPhoto

    @uploadPhoto.setter
    def uploadPhoto(self, uploadPhoto: bool):
        """
        Сеттер для установления флага, отвечающего за прикрепление фотографий к отелю

        :param uploadPhoto: флаг
        """
        self._uploadPhoto = uploadPhoto

    @property
    def countPhoto(self) -> int:
        """
        Геттер для получения количества фотографий

        :return: __countPhoto
        """
        return self._countPhoto

    @countPhoto.setter
    def countPhoto(self, countPhoto: int):
        """
        Сеттер для установления количества фотографий

        :param countPhoto: количество фотографий
        """
        self._countPhoto = countPhoto

    @property
    def sort_order(self) -> str:
        """
        Геттер для получения значения для сортировки отелей

        :return: __sort_order
        """
        return self._sort_order

    @sort_order.setter
    def sort_order(self, sort_order: str):
        """
        Сеттер для установления значения для сортировки отелей

        :param sort_order: значение для сортировки отелей
        """
        self._sort_order = sort_order

    @property
    def min_price(self) -> int:
        """
        Геттер для получения минимальной цены из диапазона

        :return: _min_price
        """
        return self._min_price

    @min_price.setter
    def min_price(self, min_price: int):
        """
        Сеттер для установления минимальной цены из диапазона

        :param min_price: минимальная цена из диапазона
        """
        self._min_price = min_price

    @property
    def max_price(self) -> int:
        """
        Геттер для получения максимальной цены из диапазона

        :return: _max_price
        """
        return self._max_price

    @max_price.setter
    def max_price(self, max_price: int):
        """
        Сеттер для установления максимальной цены из диапазона

        :param max_price: максимальная цена из диапазона
        """
        self._max_price = max_price

    @property
    def min_distance(self) -> float:
        """
        Геттер для получения минимального расстояния от центра

        :return: _min_distance
        """
        return self._min_distance

    @min_distance.setter
    def min_distance(self, min_distance: float):
        """
        Сеттер для установления минимального расстояния от центра

        :param min_distance: минимальное расстояние от центра
        """
        self._min_distance = min_distance * 0.621371

    @property
    def max_distance(self) -> float:
        """
        Геттер для получения максимального расстояния от центра

        :return: _max_price
        """
        return self._max_distance

    @max_distance.setter
    def max_distance(self, max_distance: float):
        """
        Сеттер для установления максимального расстояния от центра

        :param max_distance: максимальное расстояние от центра
        """
        self._max_distance = max_distance * 0.621371

    @property
    def currency(self) -> str:
        """
        Геттер для получения валюты

        :return: _currency
        """
        return self._currency

    @currency.setter
    def currency(self, currency: str):
        """
        Сеттер для установления валюты

        :param currency: валюта
        """
        self._currency = currency

    @property
    def arrival_date(self) -> str:
        """
        Геттер для получения даты заселения в отель

        :return: _arrival_date
        """
        return self._arrival_date

    @arrival_date.setter
    def arrival_date(self, arrival_date: str):
        """
        Сеттер для установления даты заселения в отель

        :param arrival_date: дата заселения в отель
        """
        self._arrival_date = arrival_date

    @property
    def departure_date(self) -> str:
        """
        Геттер для получения даты выезда из отеля

        :return: _departure_date
        """
        return self._departure_date

    @departure_date.setter
    def departure_date(self, departure_date: str):
        """
        Сеттер для установления даты выезда из отеля

        :param departure_date: дата выезда из отеля
        """
        self._departure_date = departure_date