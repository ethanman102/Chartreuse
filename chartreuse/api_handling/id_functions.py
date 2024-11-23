from urllib.parse import unquote

def create_user_url_id(request, id):
    id = unquote(id)
    if id.find(":") != -1:
        return id
    else:
        # create the url id
        host = request.host
        scheme = request.scheme
        return f"{scheme}://{host}/chartreuse/api/authors/{id}"
    