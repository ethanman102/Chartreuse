from urllib.parse import unquote

def create_user_url_id(request, id):
    id = unquote(id)
    if id.find(":") != -1:
        return id
    else:
        # create the url id
        host = request.get_host()
        scheme = request.scheme
        url = f"{scheme}://{host}/chartreuse/api/authors/{id}"
        return url
    