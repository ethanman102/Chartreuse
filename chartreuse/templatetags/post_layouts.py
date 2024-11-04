from django import template

register = template.Library()

@register.inclusion_tag('profile_post_varient.html')
def show_post(post,owner_id,viewer_id):
    return {"post":post,
            "owner_id" : owner_id,
            "viewer_id" : viewer_id}