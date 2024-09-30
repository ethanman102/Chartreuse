from urllib.request import urlopen
import base64
from django.http import HttpResponse, JsonResponse
from .. import models

def get_image_post(request, author_id, post_id):
    '''
    Get the image data of a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        author_id: The ID of the author of the post.
        post_id: The ID of the post.
    
    Returns:
        HttpResponse containing the image data of the post.
    '''
    if request.method == 'GET':
        post = models.Post.objects.filter(user__user__id=author_id, id=post_id).first()

        # Check if there is image data
        if (post.content and (post.contentType in ['image/jpeg;base64', 'image/png;base64'])):
            try:
                imageData = decode_image(post.content)

                return HttpResponse(imageData, content_type=post.contentType[:-7])
            except (base64.binascii.Error, ValueError):
                return JsonResponse({'error': 'Invalid image data'}, status=404)
        else:
            return JsonResponse({'error': 'Not an image'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

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