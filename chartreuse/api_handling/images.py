import base64
from urllib.request import urlopen
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .. import models
from urllib.parse import unquote

class ImageViewSet(viewsets.ViewSet):

    @extend_schema(
        summary="Gets the image data from a post",
        description=("Gets the image data from a post. The image data is returned as a base64 encoded string."),
        responses={
            200: OpenApiResponse(description="Successfully retrieved post image."),
            404: OpenApiResponse(description="Image not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @action(detail=True, methods=["GET"])
    def retrieve(self, request, author_id, post_id):
        '''
        Get the image data of a post.

        Parameters:
            request: HttpRequest object containing the request and query parameters.
            author_id: The ID of the author of the post.
            post_id: The ID of the post.
        
        Returns:
            HttpResponse containing the image data of the post.
        '''
        decoded_author_id = unquote(author_id)
        decoded_post_id = unquote(post_id)
        author = models.User.objects.filter(url_id=decoded_author_id).first()
        post = models.Post.objects.filter(user=author, url_id=decoded_post_id).first()

        if post and post.content and post.contentType in ['image/jpeg', 'image/png']:
            return JsonResponse({"content": post.content, "contentType": post.contentType}, status=200)
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
