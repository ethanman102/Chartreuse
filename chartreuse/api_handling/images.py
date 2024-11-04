import base64
from urllib.request import urlopen
from django.http import JsonResponse
from .. import models
from urllib.parse import unquote
from django.http import HttpResponse

def retrieve(request, post_id):
    '''
    Get the image data of a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        author_id: The ID of the author of the post.
        post_id: The ID of the post.
    
    Returns:
        HttpResponse containing the image data of the post.
    '''    
    decoded_post_id = unquote(post_id)
    post = models.Post.objects.filter(url_id=decoded_post_id).first()

    if post and post.content and post.contentType in ['image/jpeg', 'image/png']:
        data_url = f"data:image/png;base64, {post.content}"
        
        # Create the HTML response with the embedded image
        html_content = f"""
        <html style="height: 100%;">
            <head>
                <meta name="viewport" content="width=device-width, minimum-scale=0.1">
                <title>{post.content}</title>
            </head>
            <body style="margin: 0px; height: 100%; background-color: rgb(14, 14, 14);">
                <img style="display: block;-webkit-user-select: none;margin: auto;cursor: zoom-in;background-color: hsl(0, 0%, 90%);transition: background-color 300ms;" src="{data_url}" width="754" height="424">
            </body>
        </html>
        """
        return HttpResponse(html_content, content_type='text/html')
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
