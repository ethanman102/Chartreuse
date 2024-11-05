from django import template

# https://stackoverflow.com/questions/9472034/how-to-make-a-reusable-template-in-django#:~:text=The%20most%20flexible%20way%20to%20reuse%20template%20fragments,fragments%20that%20don%27t%20depend%20on%20the%20surrounding%20context.
# Stack Overflow Post: How to make reusable template in Django
# Purpose: Utilized to refactor the post template view in order to allow for multiple if / else template conditionals to be sortened and remain DRY
# inclusion tag suggestion as utilized by the response by Tobu on Feb 28, 2012

register = template.Library()

@register.inclusion_tag('layouts/feed_post_varient.html')
def show_feed_post(post,owner_id,viewer_id):
    return {"post":post,
            "owner_id" : owner_id,
            "viewer_id" : viewer_id}