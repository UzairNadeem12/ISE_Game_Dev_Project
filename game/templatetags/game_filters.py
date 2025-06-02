from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    try:
        return lst.index(index)
    except (ValueError, TypeError):
        return 0 