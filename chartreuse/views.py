from django.http import JsonResponse
from .models import Node
from django.shortcuts import render
import base64

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
        return JsonResponse({"error": "Missing or invalid Authorization header"}, status=401)

    try:
        # Decode the Base64-encoded credentials
        decoded_bytes = base64.b64decode(authentication.split(" ")[1])
        decoded_str = decoded_bytes.decode('utf-8')  # Convert bytes to string
        print("Decoded String", decoded_str)
        auth = decoded_str.split(":")
        username = auth[0]
        password = auth[1]
    except (IndexError, base64.binascii.Error, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid authentication format"}, status=401)

    print("Username: ", username)
    print("Password: ", password)

    host = f"{request.get_host()}/chartreuse/api/"

    node = Node.objects.filter(host=host, username=username, password=password, follow_status="INCOMING", status="ENABLED")

    if len(node) == 0:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    print("SUCCESS")

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


