import requests
from django.shortcuts import get_object_or_404
from ..models import User
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer
from rest_framework.decorators import action, api_view
from urllib.parse import unquote
from rest_framework import serializers

@extend_schema(
    summary="Gets the public events for a user from github",
    description=(
        "Gets the public events for a user from github."
        "The events are fetched from GitHub's public API and returned as a JSON object."
        "\n\n**When to use:** Use this endpoint to see recent public activities (such as commits, pull requests, issues) made by a GitHub user."
        "\n\n**How to use:** Send a GET request with the user ID in the URL. The GitHub username is extracted from the stored user data."
        "\n\n**Why to use:** Useful for tracking the public contributions and activities of a user across GitHub repositories."
        "\n\n**Why not to use:** Avoid using this if you are looking for private or non-public activity information, which is not accessible through this API."
    ),
    responses={
        200: OpenApiResponse(
            description="Successfully retrieved the public events.",
            response=inline_serializer(
                name="GitHubPublicEventsResponse",
                fields={
                    "events": serializers.ListField(
                        child=serializers.JSONField(),
                        required=True,
                        help_text="List of public events fetched from GitHub."
                    )
                }
            )
        ),
        405: OpenApiResponse(
            description="Method not allowed.",
            response=inline_serializer(
                name="MethodNotAllowedResponse",
                fields={"error": serializers.CharField(default="Method not allowed.")}
            )
        ),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def get_events(request, user_id):
    '''
    This function gets public events for a user from github. 
    https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-public-events-for-a-user

    Parameters:
        request: the request object
        user_id: the id of the user

    Returns:
        JsonResponse: the response from the github api
    '''
    if request.method == 'GET':
        decoded_user_id = unquote(user_id)
        user = get_object_or_404(User, url_id=decoded_user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/events/public")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
@extend_schema(
    summary="Gets the repositories starred by a user on github",
    description=(
        "Gets the repositories starred by a user on github."
        "The information is fetched from GitHub's API and returned as a JSON object."
        "\n\n**When to use:** Use this to get a list of repositories that a user has starred, which may indicate their interests or contributions."
        "\n\n**How to use:** Send a GET request with the user ID in the URL. The GitHub username is extracted from the stored user data."
        "\n\n**Why to use:** Helpful for understanding the repositories a user values or wants to revisit."
        "\n\n**Why not to use:** Do not use this endpoint for repositories a user owns or forks. Use the appropriate GitHub API for those."
    ),
    responses={
        # 200: OpenApiResponse(
        #     description="Successfully retrieved the public events.",
        #     examples=[
        #         {
        #             "id": "54321",
        #             "name": "awesome-repo",
        #             "html_url": "https://github.com/octocat/awesome-repo",
        #             "description": "A very useful repository.",
        #             "stargazers_count": 100
        #         }
        #     ]
        # ),
        200: OpenApiResponse(
            description="Successfully retrieved the starred repositories.",
            response=inline_serializer(
                name="GitHubStarredReposResponse",
                fields={
                    "repositories": serializers.ListField(
                        child=serializers.DictField(
                            child=serializers.CharField(),
                            help_text="A dictionary containing details of a starred repository.",
                        ),
                        required=True,
                        help_text="List of repositories starred by the user."
                    )
                }
            )
        ),
        405: OpenApiResponse(
            description="Method not allowed.",
            response=inline_serializer(
                name="MethodNotAllowedResponse",
                fields={"error": serializers.CharField(default="Method not allowed.")}
            )
        ),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def get_starred(request, user_id):
    '''
    This function gets the repositories starred by a user on github. 
    https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-repositories-starred-by-a-user

    Parameters:
        request: the request object
        user_id: the id of the user

    Returns:
        JsonResponse: the response from the github api
    '''
    if request.method == 'GET':
        decoded_user_id = unquote(user_id)
        user = get_object_or_404(User, url_id=decoded_user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/starred")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@extend_schema(
    summary="Gets the repositories watched by a user on github",
    description=(
        "Gets the repositories watched by a user on github."
        "The information is fetched from GitHub's API and returned as a JSON object."
        "\n\n**When to use:** Use this endpoint to get a list of repositories that a user is watching, typically because they are interested in staying up-to-date with its changes."
        "\n\n**How to use:** Send a GET request with the user ID in the URL. The GitHub username is extracted from the stored user data."
        "\n\n**Why to use:** Useful for understanding which repositories a user actively follows."
        "\n\n**Why not to use:** Avoid using this endpoint to retrieve information about repositories a user has starred or owns. Use the appropriate GitHub APIs for those cases."
    ),
    responses={
        # 200: OpenApiResponse(
        #     description="Successfully retrieved the public events.",
        #     examples=[
        #         {
        #             "id": "98765",
        #             "name": "interesting-repo",
        #             "html_url": "https://github.com/octocat/interesting-repo",
        #             "description": "A very interesting repository.",
        #             "watchers_count": 50
        #         }
        #     ]
        # ),
        200: OpenApiResponse(
            description="Successfully retrieved the watched repositories.",
            response=inline_serializer(
                name="GitHubWatchedReposResponse",
                fields={
                    "repositories": serializers.ListField(
                        child=serializers.DictField(
                            child=serializers.CharField(),
                            help_text="A dictionary containing details of a watched repository.",
                        ),
                        required=True,
                        help_text="List of repositories watched by the user."
                    )
                }
            )
        ),
        405: OpenApiResponse(
            description="Method not allowed.",
            response=inline_serializer(
                name="MethodNotAllowedResponse",
                fields={"error": serializers.CharField(default="Method not allowed.")}
            )
        ),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def get_subscriptions(request, user_id):
    '''
    This function gets the repositories watched by a user on github. 
    https://docs.github.com/en/rest/activity/watching?apiVersion=2022-11-28#list-repositories-watched-by-a-user

    Parameters:
        request: the request object
        user_id: the id of the user

    Returns:
        JsonResponse: the response from the github api
    '''
    if request.method == 'GET':
        decoded_user_id = unquote(user_id)
        user = get_object_or_404(User, url_id=decoded_user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/subscriptions")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)