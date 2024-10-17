'''
This function converts an uuid into a url 
'''
def create_url_from_uuid(obj, request, type):
    uri = request.build_absolute_uri("/")
    user_id = obj.user if type == "author" else obj.user.uuid
    return f"{uri}api/authors/{user_id}"


