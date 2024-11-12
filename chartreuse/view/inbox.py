from urllib.parse import unquote
from ..models import Like, User, Post, Comment
from ..views import Host
import json

def inbox(request, user_id):
    decoded_user_id = unquote(user_id)

    user = User.objects.get(pk=decoded_user_id)

    data = json.loads(request.body.decode('utf-8'))

    if (data["type"] == "author"):
        pass
    elif (data["type"] == "authors"):
        pass
    elif (data["type"] == "post"):
        pass
    elif (data["type"] == "posts"):
        pass
    elif (data["type"] == "comment"):
        pass
    elif (data["type"] == "comments"):
        pass
    elif (data["type"] == "like"):
        pass
    elif (data["type"] == "likes"):
        pass
    elif (data["type"] == "follow"):
        pass
    elif (data["type"] == "followers"):
        pass

    if(host != views.Host.host):
        # if the user is not on the current host, we need to get the user from the remote host
        api_url = host + "api/authors/" + pk
        response = requests.put(api_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

        response.raise_for_status()
        response_data = response.json()

        return JsonResponse(response_data, safe=False)