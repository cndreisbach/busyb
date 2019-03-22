from django import template

register = template.Library()


@register.simple_tag
def replace_GET_param(request, param, value):
    get_params = request.GET.copy()
    get_params[param] = value
    return f"{request.path}?{get_params.urlencode()}"
