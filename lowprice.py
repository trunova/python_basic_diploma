import requests
import re
import time
import json
import telebot
from telebot import types
from geopy.distance import geodesic
from PIL import Image
from urllib.request import urlopen


class Lowprice:
    """
    Класс, хранящий данные для поиска самых дешёвых отелей в городе

    Args:
        bot(telebot.TeleBot): передаётся бот
        sity(str): передаётся город для поиска
        countHotels(int): передаётся количество отелей
        uploadPhoto(bool): передаётся переменная, отвечающая за прикрепление фотографий к отелю
        countPhoto(int): передаётся количество фотографий
    """

    def __init__(self, bot, sity: str = ' ', countHotels: int = 0, uploadPhoto: bool = False, countPhoto: int = 0):
        self.__bot = bot
        self.__sity = sity
        self.__countHotels = countHotels
        self.__uploadPhoto = uploadPhoto
        self.__countPhoto = countPhoto


    def zeroingValues(self):
        """ Функцияс для обнуления всех параметров класса """
        self.__sity = ' '
        self.__countHotels = 0
        self.__uploadPhoto = False
        self.__countPhoto = 0


    def count(self, count: int, message: types.Message) -> bool:
        """
        Функция, устанавливающая количество отелей, и запускающая их поиск

        :param count: количество отелей
        :param message: сообщение
        :rtype: bool
        """
        if self.__countHotels == 0:
            self.countHotels = count
            return True
        elif self.__countPhoto == 0 and self.__uploadPhoto:
            self.countPhoto = count
            self.lowprice(message)
            return False


    def lowprice(self, message: types.Message):
        """
        Функция, производящая поиск отелей по заданным параметрам

        :param message: сообщение
        """

        self.__bot.send_message(message.chat.id, "Идёт поиск подходящих отелей..")
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": self.__sity.lower(), "locale": "en_US", "currency": "USD"}
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
        querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                       "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US",
                       "currency": "USD"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "7d50f060demshbf403a76fd0f28ap136b16jsne3ca74cf90e8"
        }
        response2 = requests.request("GET", url_city, headers=headers, params=querystring)
        data_hotels = json.loads(response2.text)

        new_count_hotels = 0

        for i_hotel in data_hotels.get("data").get("body").get("searchResults").get("results"):
            if self.countHotels <= new_count_hotels: break
            new_count_hotels += 1
            hotel_id = i_hotel.get("id")
            self.__bot.send_message(message.chat.id, "Отель №{i}:\nНазвание: \"{name}\"\nАдрес: {address}\nРасположение относительно центра: "
                                                    "{location} km\nЦена: {price}\nhttps://ru.hotels.com/ho{id}".format(
                i=new_count_hotels,
                name=i_hotel.get("name"),
                address=i_hotel.get("address").get("streetAddress"),
                location=round(geodesic((lon_centre, lat_centre),
                                  (i_hotel.get("coordinate").get("lon"), i_hotel.get("coordinate").get("lat"))).km, 3),
                price=i_hotel.get("ratePlan").get("price").get("current"),
                id=hotel_id))

            if self.__uploadPhoto:
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
                    requests.get(f'https://api.telegram.org/bot{self.__bot.token}/sendPhoto?chat_id={message.chat.id}&photo={img_url}')

            time.sleep(1)


    @property
    def sity(self) -> str:
        """
        Геттер для получения города

        :return: __sity
        :rtype: str
        """
        return self.__sity

    @sity.setter
    def sity(self, sity:str):
        """
        Сеттер для установления города

        :param sity: город
        """
        self.__sity = sity

    @property
    def countHotels(self) -> int:
        """
        Геттер для получения количества отелей

        :return: __countHotels
        """
        return self.__countHotels

    @countHotels.setter
    def countHotels(self, countHotels: int):
        """
        Сеттер для установления количества отелей

        :param countHotels: количество отелей
        """
        self.__countHotels = countHotels

    @property
    def uploadPhoto(self) -> bool:
        """
        Геттер для получения флага, отвечающего за прикрепление фотографий к отелю

        :return: __uploadPhoto
        """
        return self.__uploadPhoto

    @uploadPhoto.setter
    def uploadPhoto(self, uploadPhoto: bool):
        """
        Сеттер для установления флага, отвечающего за прикрепление фотографий к отелю

        :param uploadPhoto: флаг
        """
        self.__uploadPhoto = uploadPhoto

    @property
    def countPhoto(self) -> int:
        """
        Геттер для получения количества фотографий

        :return: __countPhoto
        """
        return self.__countPhoto

    @countPhoto.setter
    def countPhoto(self, countPhoto: int):
        """
        Сеттер для установления количества фотографий

        :param countPhoto: количество фотографий
        """
        self.__countPhoto = countPhoto
