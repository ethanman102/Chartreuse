from django.http import JsonResponse
from .models import Node, User
from django.shortcuts import render
import base64
import json
from urllib.parse import unquote,quote

class Host:
    _instance = None  # Class-level variable to hold the singleton instance
    host = None  # Class-level variable to hold the host value

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Host, cls).__new__(cls)
        return cls._instance

    def __init__(self, host=None):
        """Initialize the host only if it hasn't been set yet."""
        if host is not None:
            if self.host is None:
                self.host = host

def checkIfRequestAuthenticated(request):
    '''
    Purpose: Check if the request is authenticated


    Arguments:
    request: Request object
    '''
    authentication = request.headers.get('Authorization')
    
    if not authentication or not authentication.startswith('Basic'):
        # DEBUG
        # csrf_token = request.headers.get('csrfToken')
        # try:
            # if request.user.is_authenticated and csrf_token:
            #     body = json.loads(request.body)
            #     user_id = body["author_id"]

            #     user = User.objects.get(url_id=unquote(user_id))

            #     node_queryset = Node.objects.filter(host=user.host,status='ENABLED',follow_status='OUTGOING')

            #     if node_queryset.exists():
            #         JsonResponse({"success": "Authorized"}, status=200) 

            #     else:
            #         # DEBUG
            #         JsonResponse({"error": f"Query set does not exist, User: {user}... user_id: {user_id}"}, status=401)


            # else:
            #     # DEBUG
            #     JsonResponse({"error": f"csrfToken: {csrf_token}, is authenticated: {request.user.is_authenticated}"}, status=401)         

        # except Exception as e:
        #     return JsonResponse({"error": f"Missing or invalid Authorization header: {e}"}, status=401)
        
        # finally: 
        return JsonResponse({"error": "Missing or invalid Authorization header"}, status=401)

    try:
        # Decode the Base64-encoded credentials
        decoded_bytes = base64.b64decode(authentication.split(" ")[1])
        decoded_str = decoded_bytes.decode('utf-8')  # Convert bytes to string
        auth = decoded_str.split(":")
        username = auth[0]
        password = auth[1]
    except (IndexError, base64.binascii.Error, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid authentication format"}, status=401)

    node = Node.objects.filter(username=username, password=password, follow_status="INCOMING", status="ENABLED")
    if len(node) == 0:
        
        return JsonResponse({"error": "Unauthorized"}, status=401)

    
    return JsonResponse({"success": "Authorized"}, status=200)


def error(request):
    '''
    Purpose: View to render a generic error page


    Arguments:
    request: Request object
    '''
    return render(request, 'error.html')

def test(request):
    '''
    Purpose: View to render a test page

    Test page is used for testing UI changes


    Arguments:
    request: Request object
    '''
    test_str = """
    
    # Hello <br> 
    and 
     
    **goodbye** 
    """
    return render(request, 'test.html', {'markdown_txt': test_str})


