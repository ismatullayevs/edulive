from django.conf import settings
from random import randint
from django.core.cache import cache
from datetime import datetime


class OTP:
    def __init__(self, key, data=None, **kwargs):
        """key userning session codi. Data forma fieldlari to'plami """

        self.__session_user_key = key
        self.__data = data

        if self.__data is not None:
            # forma ma'lumotlari
            cache.set(self.__session_user_key, self.__data, 60*10, version=1)

            # cache codi verifikatsiya ma'lumotlari'
            cache.set(self.__session_user_key, {
                'code': randint(10000, 99999),
                'time': str(datetime.now()),
            }, 60*10, version=2)


            # sanoq

            cache.set(self.__session_user_key, 1, 60*10, version=3)
           # cache.set(self.__session_user_key, 1, 60 * 10, version=3)
           # version1 = cache.get(self.__session_user_key,version=1)
           # version2 = cache.get(self.__session_user_key,version=2)
           # version3 = cache.get(self.__session_user_key,version=3)
           # print(version1, version2, version3)
        try:
            self.__form = cache.get(self.__session_user_key, version=1)
            self.__code = cache.get(self.__session_user_key, version=2)
            self.__count = cache.get(self.__session_user_key, version=3)
        except:
            self.__form = None
            self.__code = None
            self.__count = None

    @property
    def resend(self):
        if cache.get(self.__session_user_key, version=3) and cache.get(self.__session_user_key, version=1):
            cache.set(self.__session_user_key, {
                'code': randint(10000, 99999),
                'time': str(datetime.now()),
            }, 60 * 10, version=2)

            cache.incr(self.__session_user_key, version=3)
            cache.touch(self.__session_user_key, 60 * 10, version=3)
            cache.touch(self.__session_user_key, 60 * 10, version=1)

            self.__form = cache.get(self.__session_user_key, version=1)
            self.__code = cache.get(self.__session_user_key, version=2)
            self.__count = cache.get(self.__session_user_key, version=3)
        else:
            cache.delete(self.__session_user_key, version=1)
            cache.delete(self.__session_user_key, version=2)
            cache.delete(self.__session_user_key, version=3)

    @property
    def get_otp(self):
        try:
            code = self.__code['code']
        except:
            code = None
        return str(code)

    @property
    def get_phone(self):
        try:
            phone = str(self.__form['data']['phone_number'])
        except:
            phone = None
        return phone

    @property
    def count(self):
        return str(self.__count)

    def get_form(self):
        return dict(self.__form)

    def __str__(self):
        try:
            code = str(self.__code['code'])
        except:
            code = None
        return code
