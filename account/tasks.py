from celery import shared_task
from django.core.mail import send_mail
from django.core.cache import cache
from random import randint

from datetime import datetime
from get_sms import Getsms

# asinxron sms yuborish

@shared_task
def verify(key):
    object_code = cache.get(key)

    if object_code is not None:
        cache.delete(key)
        data = {
            'date': datetime.now(),
            'code': randint(10000, 99999)
        }
        key = cache.set(key, data, 600)
    else:
        data = {
            'date': datetime.now(),
            'code': randint(10000, 99999)
        }
        key = cache.set(key, data, 600)
    return key


@shared_task
def send_sms(phone, text):
    # GetSMS
    login = 'Stable'
    password= '51v4N0y4R3N5rbcy122c'
    message = Getsms(login=login, password=password)
    phone_number = phone
    results = message.send_message(phone_number, text=text)



#@shared_task
#def send_email(email, code):
#    mail_send = send_mail(subject='subject', message=str(code), from_email='narziyev@gmail.com',
#                          recipient_list=[email])
    # mail_send = send_mail(
    #     'subject',
    #     code,
    #     email
    # )
#    return mail_send
    # res = send_mail(code, code_user, settings.EMAIL_HOST_USER, [email])
