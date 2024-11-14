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

    basic = authentication.split(" ")
    if basic[0] != "Basic":
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    # Decode the Base64-encoded credentials
    try:
        decoded_bytes = base64.b64decode(basic[1])
        decoded_str = decoded_bytes.decode('utf-8')  # Convert bytes to string
    except (base64.binascii.Error, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid authentication format"}, status=401)

    auth = decoded_str.split(":")
    if len(auth) != 2:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    username = auth[0]
    password = auth[1]

    host = request.get_host

    node = Node.objects.filter(host=host, username=username, password=password)

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


