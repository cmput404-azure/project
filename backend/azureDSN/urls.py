from django.urls import path
from .views import *
from .views import likes

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path("", index, name="index"),

    # Single Author API
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    
    # Posts API
    path("api/posts/<uuid:post_fqid>/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),

    # Likes API
    path("api/authors/<uuid:author_serial>/inbox/", likes.send_like, name="send_like"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/likes/", likes.get_likes_by_serial, name="get_likes_serial"),
]
