from django import template
register = template.Library()

@register.filter(name='variation_since_last')
def variation_since_last(value):
    val_str = '{}'.format(value)
    if float(value) > 0:
        return '{} más'.format(val_str)
    else:
        return '{} menos'.format(val_str.replace('-',''))
