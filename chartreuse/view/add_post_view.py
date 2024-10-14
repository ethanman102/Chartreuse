from django.http import JsonResponse
from django.shortcuts import render, redirect
from chartreuse.models import User, Post
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

def add_post(request):
    return render(request, 'add_post.html')

@csrf_exempt
def save_post(request):
    if request.method == 'POST':
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated."}, status=401)

        # Get the current user
        current_user = request.user
        current_user_model = get_object_or_404(User, user=current_user)

        # Get the form values
        post_type = request.POST.get("visibility", "PUBLIC")
        post_title = request.POST.get("title")
        post_description = request.POST.get("description")
        contentType_description = request.POST.get("contentType", "text/plain")
        content_description = request.POST.get("content")

        # Validate the required fields
        if not post_title:
            return JsonResponse({"error": "Post title is required."}, status=400)

        if not content_description:
            return JsonResponse({"error": "Post content is required."}, status=400)

        # Create and save the post
        post = Post(user=current_user_model, title=post_title, description=post_description, contentType=contentType_description, content=content_description, visibility=post_type)
        post.save()

        # Redirect to homepage after saving the post
        return redirect('/chartreuse/homepage')  # Make sure 'homepage' URL name is correct in your urls.py

    # If method is not POST, you should ideally return a proper response
    return JsonResponse({"error": "Invalid request method. POST required."}, status=405)
