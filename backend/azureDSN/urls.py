from django.urls import path
from .views import *
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.generic import TemplateView
from azureDSN.views import index

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    # re_path(r"^(?P<path>.*)$", index, {"document_root": settings.REACT_APP_BUILD_PATH}),
    path('', TemplateView.as_view(template_name='index.html')),
  
    # Inbox API
    path("api/authors/<uuid:author_serial>/inbox/", InboxView.as_view(), name="inbox"),
    
    # path("", index, name="index"),
    # path("api/posts/{POST_FQID}/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    path("api/authors/all/", AuthorsCompleteView.as_view(), name="authors"),

    # Posts API
    path("api/posts/<uuid:post_fqid>/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),

    # Follow API

    path('api/authors/<uuid:user_id>/followers/', FollowGetView.as_view(), name='followers'),
    path('api/authors/<uuid:user_id>/followers/<path:follower_url>/', FollowChangeView.as_view(), name='followers_handler'),  
    path('api/authors/<uuid:user_id>/following/', FollowingView.as_view(), name='following'),  

    # Likes API
    # path("api/authors/<uuid:author_serial>/inbox/", likes.send_like, name="send_like"),
    # path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/likes/", likes.get_likes_by_serial, name="get_likes_serial"),
    
    path("api/authors/<uuid:author_serial>/liked/", AuthorLikesView.as_view(), name="author_likes_by_serial"),
    # path("api/authors/<str:author_fqid>/liked/", AuthorLikesView.as_view(), name="author_likes_by_fqid"),

    path("api/liked/<uuid:like_fqid>/", SingleLikeView.as_view(), name="get_like_by_fqid"),
    path("api/authors/<uuid:author_serial>/liked/<uuid:like_serial>/", SingleLikeView.as_view(), name="get_like_by_serial")
]

