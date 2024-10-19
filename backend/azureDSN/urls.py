from django.urls import path

from .views.comments import SingleCommentView, MultipleCommentsView
from .views import *
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.generic import TemplateView
from azureDSN.views import index

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
  
    # Inbox API
    path("api/authors/<uuid:author_serial>/inbox/", InboxView.as_view(), name="inbox"),
    
    # path("", index, name="index"),
    # path("api/posts/{POST_FQID}/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/", AuthorsView.as_view(), name="authors"),
    
    # ======================================
    path("api/authors/all/", AuthorsCompleteView.as_view(), name="authors"),
  
    # Posts API
    path("api/posts/<uuid:post_fqid>/", PostView.as_view(), name="post"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),

    # Follow API

    path('api/authors/<uuid:user_id>/followers/<path:follower_url>/', FollowView.as_view(), name='followers_handler'),  
    path('api/authors/<uuid:user_id>/followers/', FollowView.as_view(), name='followers_handler'),  

    path('api/authors/<uuid:user_id>/following/', FollowCustomView.as_view(), name='following'),  

    # ======================================
    # Likes API
    path("api/authors/<uuid:author_serial>/inbox/", LikeView.as_view(), name="send_like"),

    # Getting a single Like object
    path("api/authors/<uuid:author_serial>/liked/<uuid:like_serial>/", LikeView.as_view(), name="get_like_by_serial"),
    path("api/liked/<path:like_fqid>/", LikeView.as_view(), name="get_like_by_fqid"),
    
    # Getting Likes that belong to an Author
    path("api/authors/<uuid:author_serial>/liked/", AuthorLikesView.as_view(), name="author_likes_by_serial"),
    path("api/authors/<path:author_fqid>/liked/", AuthorLikesView.as_view(), name="author_likes_by_fqid"),

    # path("api/liked/<uuid:like_fqid>/", SingleLikeView.as_view(), name="get_like_by_fqid"),
    # path("api/authors/<uuid:author_serial>/liked/<uuid:like_serial>/", SingleLikeView.as_view(), name="get_like_by_serial")
    
    # Comments API
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments", MultipleCommentsView.as_view(), name="multiple_comment_view_by_postid"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comment/<str:comment_fqid>", SingleCommentView.as_view(), name="single_comment_view_by_fqid"),

    
    path("api/posts/<str:post_fqid>/comments", AuthorLikesView.as_view(), name="author_likes_by_fqid"),

    # Getting Likes that belong to a Post or Comment (TBD)
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/likes/", LikesView.as_view(), name="get_likes_by_serial"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments/<uuid:comments_serial>/likes", LikesView.as_view(), name="get_comment_likes"),
]

