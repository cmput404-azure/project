from django.urls import path
from .views import *


# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    # path("/api/authors/<uuid:user_id>/inbox/", InboxView.as_view(), name="inbox")
    path("", index, name="index"),
    # path("api/posts/{POST_FQID}/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),
    path('api/authors/<uuid:user_id>/followers/', FollowView.as_view(), name='followers'),
    path('api/authors/<uuid:user_id>/followers/<follower_id>/add/', FollowView.add_follower , name='add_follower'),
    # path("api/authors/", AuthorsView.as_view(), name="authors"),
]
