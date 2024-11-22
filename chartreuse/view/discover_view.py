from django.shortcuts import redirect, get_object_or_404
from chartreuse.models import User,Node
from django.views.generic.list import ListView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote
import requests
import base64
import json


PAGE_SIZE = 5

# ListView class based view discovered via youtube video: https://www.youtube.com/watch?v=dHvcioGHg08
# Title of Youtube Video: Learn Django Class Based Views - ListView Theory and Examples
# Creator: Very Academy, on August 29, 2020

class DiscoverAuthorListView(ListView):
    model = User
    template_name = "discover_author.html"
    context_object_name= "authors"


    def get_context_data(self,**kwargs):
        '''
        Uses the pagination API to get the authors for the current discover menu for nodes we connect with
        '''
        context =  super().get_context_data(**kwargs)
        authors = context.get('authors',[])

        authors = self.discover(authors)
    
        context['host'] = self.kwargs.get('host','')
        context['authors'] = authors

        current_auth_user = self.request.user
        current_user_model = User.objects.get(user=current_auth_user)

        context['current_user_url_id'] = quote(current_user_model.url_id,safe='')


        if len(context['authors']) == PAGE_SIZE:
            context['has_next'] = True
        else:
            context['has_next'] = False
        
        page_num =  int(self.request.GET.get('page'))

        if page_num > 1:
            context['has_first'] = True
            context['has_previous'] = True
        else:
            context['has_first'] = False
            context['has_previous'] = False
        

        context['page_number'] = page_num
        context['item_amount'] = len(authors)
        context['page_size'] = PAGE_SIZE


        return context



    def get_queryset(self):
        page = int(self.request.GET.get('page',1))
        host = self.kwargs['host']

        host = unquote(host) # un percent encode the host name!
    
        node = Node.objects.filter(host=host,follow_status='OUTGOING')

        if not node.exists():
            return []
        
        node = node[0]
        
        username = node.username
        password = node.password

        url = host
        if not host.endswith('api/'):
            url += 'api/'
        url += 'authors/'

        params = {
            'page':page,
            'size':PAGE_SIZE
        }   

        user = self.request.user
        user_object = User.objects.get(user=user)

        headers = {
            "X-Original-Host": user_object.host
        }

        print(f"user: {user}")

        response = requests.get(url, params=params, auth=(username,password), headers=headers)       
        
        if response.status_code != 200:
            return []
        else:
            response_data = json.loads(response.content)
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
                    remote_author = node_author_queryset[0]
                    remote_author.url_id = quote(remote_author.url_id,safe='')
                    author_list.append(remote_author)
                else:
                    # author has not be discovered by our node yet, so must be appended to user database.
                    remote_author = User.objects.create(
                        url_id = url_id,
                        displayName = author.get('displayName',''),
                        host = author.get('host'),
                        github = author.get('github',''),
                        profileImage = author.get('profileImage',''),
                    )

                    remote_author.url_id = quote(remote_author.url_id,safe='')

                    author_list.append(remote_author)

        return author_list
    
class DiscoverNodeListView(ListView):
    template_name = 'discover_node.html'
    model = Node
    context_object_name = 'nodes'
    queryset = Node.objects.filter(follow_status='OUTGOING', status='ENABLED')

    def get_context_data(self, **kwargs):
        '''
        Purpose: use the outgoing Node connections to grab their hostnames for population
        '''

        context =  super().get_context_data(**kwargs)
        hostnames = [quote(node.host,safe='') for node in context['nodes']]
        context['hostnames'] = hostnames
        return context

                




