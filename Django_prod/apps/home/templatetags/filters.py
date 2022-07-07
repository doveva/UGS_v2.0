from django import template
register = template.Library()

@register.filter
def dict_index(list_value, list_indexation):
    return list_value[str(list_indexation)]


@register.filter
def list_index(list_value, list_indexation):
    return list_value[int(list_indexation)]

@register.filter(name='array_to_string')
def array_to_string(array):
    return ''.join(array)