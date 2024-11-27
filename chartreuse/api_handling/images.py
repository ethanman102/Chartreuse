import base64
from urllib.request import urlopen
from django.http import JsonResponse
from .. import models
from urllib.parse import unquote
from django.shortcuts import redirect
from pathlib import Path
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer
from rest_framework.decorators import action, api_view
from rest_framework import serializers

@extend_schema(
    summary="Retrieve and serve an image from a post on the homepage",
    description=(
        "Fetches the image data associated with a specific post ID, decodes it, saves it locally, and serves the image via a static URL."
        "\n\n**When to use:** Use this endpoint to retrieve an image attached to a specific post. The post must contain a valid image content type (`image/jpeg` or `image/png`) and base64-encoded image data."
        "\n\n**How to use:** Send a GET request with the `post_id` in the URL path. The server will process the image data and redirect to a static URL serving the image."
        "\n\n**Why to use:** This endpoint provides a way to decode, store, and serve images associated with posts."
        "\n\n**Why not to use:** Avoid using if the post does not contain an image or the content type is unsupported."
    ),
    parameters=[
        {
            "name": "post_id",
            "in": "path",
            "description": "The ID of the post whose image is to be retrieved.",
            "required": True,
            "schema": {
                "type": "string"
            }
        }
    ],
    responses={
        302: OpenApiResponse(
            description="Image successfully retrieved and served.",
            response=inline_serializer(
                name="RedirectResponse",
                fields={
                    "redirect": serializers.CharField(default="/static/images/<post_id>.png")
                }
            )
        ),
        404: OpenApiResponse(
            description="Post not found or does not contain a valid image.",
            response=inline_serializer(
                name="ImageNotFoundResponse",
                fields={
                    "error": serializers.CharField(default="Not an image.")
                }
            )
        )
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
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

    if post and post.content and post.contentType in ['image/jpeg;base64', 'image/png;base64']:
        # Decode base64 image data from the post content
        image_data = post.content.split(',',1)[1]
        image_data = base64.b64decode(post.content)

        # Define the path for saving the image
        images_dir = Path("chartreuse/static/images")
        images_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        if post.contentType == 'image/jpeg;base64':
            suffix = '.jpg'
        else:
            suffix = '.png'
        image_path = images_dir / f"{post.id}{suffix}"  # Save as .png based on post content type

        # Write the decoded image data to the file
        with image_path.open("wb") as f:
            f.write(image_data)

        # Redirect to the saved image
        return redirect(f"/static/images/{post.id}{suffix}")
    else:
        return JsonResponse({'error': 'Not an image'}, status=404)

@extend_schema(
    summary="Retrieve and serve an image from a post on an author's profile",
    description=(
        "Fetches the image data associated with a specific post ID for a given author, decodes it, saves it locally, and serves the image via a static URL."
        "\n\n**When to use:** Use this endpoint to retrieve an image attached to a specific post from a particular author's profile. The post must contain a valid image content type (`image/jpeg` or `image/png`) and base64-encoded image data."
        "\n\n**How to use:** Send a GET request with the `author_id` and `post_id` in the URL path. The server will process the image data and redirect to a static URL serving the image."
        "\n\n**Why to use:** This endpoint provides a way to decode, store, and serve images associated with posts from an author's profile."
        "\n\n**Why not to use:** Avoid using if the post does not contain an image or the content type is unsupported."
    ),
    parameters=[
        {
            "name": "author_id",
            "in": "path",
            "description": "The ID of the author whose post's image is to be retrieved.",
            "required": True,
            "schema": {
                "type": "string"
            }
        },
        {
            "name": "post_id",
            "in": "path",
            "description": "The ID of the post whose image is to be retrieved.",
            "required": True,
            "schema": {
                "type": "string"
            }
        }
    ],
    responses={
        302: OpenApiResponse(
            description="Image successfully retrieved and served.",
            response=inline_serializer(
                name="RedirectResponse",
                fields={
                    "redirect": serializers.CharField(default="/static/images/<post_id>.png")
                }
            )
        ),
        404: OpenApiResponse(
            description="Post not found or does not contain a valid image.",
            response=inline_serializer(
                name="ImageNotFoundResponse",
                fields={
                    "error": serializers.CharField(default="Not an image.")
                }
            )
        )
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def retrieve_from_profile(request, author_id, post_id):
    '''
    Get the image data of a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        post_id: The ID of the post.
    
    Returns:
        HttpResponse containing the image data of the post.
    '''    
    if author_id.isdigit() and post_id.isdigit(): # given serials
        decoded_post_id = create_post_url_id(request,author_id,post_id)
    else: # given FQID
        decoded_post_id = unquote(post_id)
    post = models.Post.objects.filter(url_id=decoded_post_id).first()

    if post and post.content and post.contentType in ['image/jpeg;base64', 'image/png;base64']:
        # Decode base64 image data from the post content
        image_data = post.content.split(',',1)[1]
        image_data = base64.b64decode(image_data)

        # Define the path for saving the image
        images_dir = Path("chartreuse/static/images")
        images_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        if post.contentType == 'image/jpeg;base64':
            suffix = '.jpg'
        else:
            suffix = '.png'
        image_path = images_dir / f"{post.id}{suffix}"  # Save as .png based on post content type

        # Write the decoded image data to the file
        with image_path.open("wb") as f:
            f.write(image_data)

        # Redirect to the saved image
        return redirect(f"/static/images/{post.id}{suffix}")
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
    
def create_post_url_id(request, author_id,post_id):
        host = request.get_host()
        scheme = request.scheme
        url = f"{scheme}://{host}/chartreuse/api/authors/{author_id}/posts/{post_id}"
        return url
