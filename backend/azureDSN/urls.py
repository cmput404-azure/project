from django.urls import path
from .views import *

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path("", index, name="index"),

    # Single Author API
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),
]
