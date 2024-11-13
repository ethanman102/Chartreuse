from django.shortcuts import redirect, get_object_or_404
from chartreuse.models import User,Node
from django.views.generic.list import ListView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote
import requests
import base64
import json

PAGE_SIZE = 10

# ListView class based view discovered via youtube video: https://www.youtube.com/watch?v=dHvcioGHg08

class DiscoverAuthorListView(ListView):
    model = User
    template_name = "discover.html"
    context_object_name= "authors"
    paginate_by = PAGE_SIZE


    def get_context_data(self,**kwargs):
        '''
        Uses the pagination API to get the authors for the current discover menu for nodes we connect with
        '''
        pass


    def get_queryset(self):
        page = self.request.GET.get('page',1)
        host = self.kwargs.get('host')

        host = unquote('host') # un percent encode the host name!

        node = Node.objects.filter(host=host,connection='OUTGOING')
        if not node.exists():
            return []
        
        username = base64.b64encode(node.get('username','')).decode('utf-8')
        password = base64.b64decode(node.get('password','')).decode('utf-8')

        url = f'https://{host}/api/authors/'

        headers = {
            'Authorization' : 'Basic {username}:{password}'
        }

        params = {
            'page':page,
            'size':self.paginate_by
        }

        response = requests.get(url,headers=headers,params=params)
        
        if response.status_code != 200:
            return []
        else:
            response_data = json.loads(response.body)
            author_data = response_data.get('authors',[])

        return author_data

    

    def discover(self,authors):
        '''
        
        Purpose: Discovers an author fetched from the node, if this author is not discovered (in this node's database) add it,
        else continue.

        Arguments: 
        authors: a list of dictionaries containing the json data of the authors to be discovered.
        
        '''

        author_list = []

        for author in authors:

            url_id = author.get('id')

            if url_id != None:
                node_author_queryset = User.objects.filter(url_id=url_id)

                if node_author_queryset.exists():
                    author_list.append(node_author_queryset[0])
                else:
                    # author has not be discovered by our node yet, so must be appended to user database.
                    remote_author = User.objects.create(
                        url_id = url_id,
                        displayName = author.get('displayName',''),
                        host = author.get('host'),
                        github = author.get('github',''),
                        profileImage = author.get('profileImage',''),
                    )

                    author_list.append(remote_author)

        return author_list
                




