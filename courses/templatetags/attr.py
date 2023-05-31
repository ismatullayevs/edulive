from django import template

register = template.Library()


@register.filter(name='add_attr')
def attr(value, arg, attr='placeholder'):
    css_classes = value.field.widget.attrs.get(attr, '')
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    args = arg.split(' ')
    for a in args:
        if a not in css_classes:
            css_classes.append(a)
    return value.as_widget(attrs={attr: ' '.join(css_classes)})


@register.filter(name='add_value')
def value(value, arg, attr='value'):
    css_classes = value.field.widget.attrs.get(attr, '')
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    args = arg.split(' ')
    for a in args:
        if a not in css_classes:
            css_classes.append(a)
    return value.as_widget(attrs={attr: ' '.join(css_classes)})


@register.filter(name='add_class')
def value(value, arg, attr='class'):
    css_classes = value.field.widget.attrs.get(attr, '')
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    args = arg.split(' ')
    for a in args:
        if a not in css_classes:
            css_classes.append(a)
    return value.as_widget(attrs={attr: ' '.join(css_classes)})
