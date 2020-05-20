from django import template
register = template.Library()

# Here, register is a django.template.Library instance, as before
@register.inclusion_tag('dashboard/templatetags/CCAA_growthplots.html')
def renderRegionsGrowth(regions):
    return {'regions': regions}
