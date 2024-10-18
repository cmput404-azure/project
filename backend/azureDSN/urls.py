from django.urls import path

from .views import *
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings

# from .utils.fqid_checker_util import author_likes_dispatch

from azureDSN.views import index

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    # re_path(r"^(?P<path>.*)$", index, {"document_root": settings.REACT_APP_BUILD_PATH}),
  
    # path("/api/authors/<uuid:user_id>/inbox/", InboxView.as_view(), name="inbox")
    path("", index, name="index"),
    # path("api/posts/{POST_FQID}/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    
    # Posts API
    path("api/posts/<uuid:post_fqid>/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),

    # ======================================
    # Likes API
    path("api/authors/<uuid:author_serial>/inbox/", LikeView.as_view(), name="send_like"),

    # Getting a single Like object
    path("api/authors/<uuid:author_serial>/liked/<uuid:like_serial>/", LikeView.as_view(), name="get_like_by_serial"),
    path("api/liked/<path:like_fqid>/", LikeView.as_view(), name="get_like_by_fqid"),
    
    # Getting Likes that belong to an Author
    path("api/authors/<uuid:author_serial>/liked/", AuthorLikesView.as_view(), name="author_likes_by_serial"),
    path("api/authors/<path:author_fqid>/liked/", AuthorLikesView.as_view(), name="author_likes_by_fqid"),

    # Getting Likes that belong to a Post or Comment (TBD)
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/likes/", LikesView.as_view(), name="get_likes_by_serial"),
    path("api/posts/<path:post_fqid>/likes/", LikesView.as_view(), name="get_likes_by_fqid"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments/<uuid:comments_serial>/likes", LikesView.as_view(), name="get_comment_likes"),
]
