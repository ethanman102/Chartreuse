from django import template

register = template.Library()

@register.inclusion_tag('singular_post_varient.html',takes_context=True)
def show_singular_post(context):
    return context
