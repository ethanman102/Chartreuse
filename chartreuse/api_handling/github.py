import requests
from django.shortcuts import get_object_or_404
from ..models import User
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action, api_view

@extend_schema(
    summary="Gets the public events for a user from github",
    description=("Gets the public events for a user from github. The events are returned as a JSON object."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved the public events.",),
        405: OpenApiResponse(description="Method not allowed."),
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
        user = get_object_or_404(User, id=user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/events/public")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
@extend_schema(
    summary="Gets the repositories starred by a user on github",
    description=("Gets the repositories starred by a user on github. The repositories are returned as a JSON object."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved the public events.",),
        405: OpenApiResponse(description="Method not allowed."),
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
        user = get_object_or_404(User, id=user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/starred")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@extend_schema(
    summary="Gets the repositories watched by a user on github",
    description=("Gets the repositories watched by a user on github. The repositories are returned as a JSON object."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved the public events.",),
        405: OpenApiResponse(description="Method not allowed."),
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
        user = get_object_or_404(User, id=user_id)

        githubUrl = user.github
        githubUsername = githubUrl.split("/")[-1]

        response = requests.get(f"https://api.github.com/users/{githubUsername}/subscriptions")

        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)