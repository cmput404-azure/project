def create_url_from_uuid(obj, request, type):
    uri = request.build_absolute_uri("/")
    user_id = obj.user_id if type == "author" else obj.author.user_id
    return f"{uri}api/authors/{user_id}"