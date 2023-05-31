from django import template
from django.http import HttpResponse

from courses.models import Course
from account.models import Students

register = template.Library()


@register.simple_tag(name='profil')
def account(user):
    try:
        std = Students.objects.get(user=user)
        return std
    except:
        return ''
