import base64
from urllib.request import urlopen
from django.http import JsonResponse
from .. import models
from urllib.parse import unquote
from django.shortcuts import redirect
from pathlib import Path

def retrieve_from_homepage(request, post_id):
    '''
    Get the image data of a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        post_id: The ID of the post.
    
    Returns:
        HttpResponse containing the image data of the post.
    '''    
    decoded_post_id = unquote(post_id)
    post = models.Post.objects.filter(url_id=decoded_post_id).first()

    if post and post.content and post.contentType in ['image/jpeg', 'image/png']:
        # Decode base64 image data from the post content
        image_data = base64.b64decode(post.content)

        # Define the path for saving the image
        images_dir = Path("chartreuse/static/images")
        images_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        image_path = images_dir / f"{post.id}.png"  # Save as .png based on post content type

        # Write the decoded image data to the file
        with image_path.open("wb") as f:
            f.write(image_data)

        # Redirect to the saved image
        return redirect(f"/static/images/{post.id}.png")
    else:
        return JsonResponse({'error': 'Not an image'}, status=404)

def retrieve_from_profile(request, author_id, post_id):
    '''
    Get the image data of a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        post_id: The ID of the post.
    
    Returns:
        HttpResponse containing the image data of the post.
    '''    
    decoded_post_id = unquote(post_id)
    post = models.Post.objects.filter(url_id=decoded_post_id).first()

    if post and post.content and post.contentType in ['image/jpeg', 'image/png']:
        # Decode base64 image data from the post content
        image_data = base64.b64decode(post.content)

        # Define the path for saving the image
        images_dir = Path("chartreuse/static/images")
        images_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        image_path = images_dir / f"{post.id}.png"  # Save as .png based on post content type

        # Write the decoded image data to the file
        with image_path.open("wb") as f:
            f.write(image_data)

        # Redirect to the saved image
        return redirect(f"/static/images/{post.id}.png")
    else:
        return JsonResponse({'error': 'Not an image'}, status=404)


def encode_image(image_path):
    '''
    Encode an image into a base64 string.

    Parameters:
        image_path: The path to the image file.

    Returns:
        The base64 encoded string.
    '''
    try:
        # Try to open as a local file first
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    except:
        # If not found locally, assume it's a URL
        try:
            with urlopen(image_path) as url:
                f = url.read()
                encoded_string = base64.b64encode(f).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to retrieve image from URL: {e}")
    
    return encoded_string

def decode_image(encoded_string):
    '''
    Decode an image from a base64 string.

    Parameters:
        encoded_string: The base64 encoded string.

    Returns:
        The image data.
    '''
    try:
        imageData = base64.b64decode(encoded_string)

        return imageData
    except Exception as e:
        raise ValueError(f"Failed to decode image: {e}")
