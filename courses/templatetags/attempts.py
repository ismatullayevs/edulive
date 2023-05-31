from django import template

register = template.Library()


@register.filter(name='atm')
def attempt(obj, user=None):
    try:
        a = obj.filter(student__user=user).last()
        return a.attempts
    except:
        return 0

@register.filter()
def score(obj, user=None):
    try:
        a = obj.filter(student__user=user).last()
        return int(a.score)
    except:
        return 0

@register.simple_tag(name='sert')
def sert(obj, *args, **kwargs):
    a = obj.filter(student__user=kwargs['user'], course=kwargs['course']).last()
    if a:
        return a.uuid
    else:
        return 0


@register.filter()
def digit(obj):
    return '{:0>8}'.format(obj)
