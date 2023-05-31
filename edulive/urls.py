"""edulive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import random
import time
from django.views.static import serve

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static
from account.models import CustomUser, Students
from get_sms import Getsms
from faker import Faker
from account.forms import RegisterUserForm
from django.http import HttpResponse
from get_sms import Getsms
from django.http import HttpResponse
#
# def create_user(request):
#     students = CustomUser.objects.all()[:100]

# for x in students:
#     Students.objects.create(user=x)
# fake = Faker()
# for x in range(1000):
#
#     name = fake.name()
#     if len(name.split(' '))==2:
#         username = str(name).split(' ')[0].lower()
#         phone_number = "99899000{:04d}".format(x)
#
#         data = {
#             'username': username,
#             'phone_number': phone_number,
#             'full_name': f"{name} {username.capitalize()}",
#             'email': fake.email(),
#             'password1': 'admin111',
#             'password2': 'admin111',
#         }
#         form = RegisterUserForm(data)
#         print(form.is_valid())
#         if form.is_valid():
#             print('valid')
#             form.save()
#             print('save')

# return redirect('course:homepage')
def send_s(request):
    login = 'Stable'
    password = '51v4N0y4R3N5rbcy122c'
    message = Getsms(login=login, password=password)
    phone = ['998997047646']
    result = message.send_message(phone_numbers=phone, text=f"sizning verifikatsiya kodingiz {123456}")
    return HttpResponse(result)
urlpatterns = [
    path('mvzona/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('news/', include('news.urls')),
    path('quiz/', include('quiz.urls')),
    path('create/', send_s),
    path('', include('courses.urls')),

    #path('__debug__/', include('debug_toolbar.urls')),
   #path('create/', sms_send, name='create')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),]

if settings.DEBUG:
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),
    urlpatterns += static(settings.MEDIA_URL,
                        document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                        document_root=settings.STATIC_ROOT)

#urlpatterns += static(settings.MEDIA_URL,
#                      document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_URL,
#                      document_root=settings.STATIC_ROOT)
#
