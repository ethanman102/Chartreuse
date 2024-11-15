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
    print("Auth: ", authentication)

    basic = authentication.split(" ")
    print(basic)

    auth = basic[1].split(":")
    
    username = auth[0]
    password = auth[1]

    host = request.get_host
    print("Host: ", host)
    print(Node.objects.all())

    node = Node.objects.filter(host=host, username=username, password=password)
    print("MADE IT")

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


