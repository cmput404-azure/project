from django.urls import path
from .views import *
from .views.posts import * # raises warning for PostCreation if not imported
from django.urls import path
from django.urls import re_path
from django.views.generic import TemplateView

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path('api/stream/', PublicStreamView.as_view(), name='stream'),
    path('api/stream/auth/', AuthStreamView.as_view(), name='auth_stream'),
    
    # Follow API
    path('api/authors/<uuid:user_id>/followers/<path:follower_url>/', FollowView.as_view(), name='followers_handler'),  
    path('api/authors/<uuid:user_id>/followers/', FollowerView.as_view(), name='get_followers'),
    path('api/authors/<int:user_id>/followers/', FollowerView.as_view(), name='get_followers_integer'),
    path('api/authors/<uuid:user_id>/following/', FollowCustomView.as_view(), name='following'),  

    # Inbox API
    path("api/authors/<uuid:author_serial>/inbox/", InboxView.as_view(), name="inbox"),
    path("api/authors/<int:author_serial>/inbox/", InboxView.as_view(), name="inbox_integer"), # To connect with other groups with integer id
    path("api/authors/<uuid:author_serial>/inbox", InboxView.as_view(), name="inbox_no_slash"), # Other groups might call this
    path("api/authors/<uuid:author_serial>/inbox/paginated/", PaginatedInboxView.as_view(), name="paginated_inbox"),

    # Remote API
    path("api/authors/recommended/", RemoteAuthorsView.as_view(), name="get_recommended_authors"),
    path("api/check/<uuid:local_serial>/follows/<path:remote_fqid>/", RemoteFolloweeView.as_view(), name="check_following_status"),

    # Likes on Posts or Comments
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/likes/", LikesView.as_view(), name="get_likes_by_serial"),
    path("api/authors/<int:author_serial>/posts/<uuid:post_serial>/likes/", LikesView.as_view(), name="get_likes_by_serial_int"),
    path("api/posts/<path:post_fqid>/likes/", LikesView.as_view(), name="get_likes_by_fqid"),
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments/<path:comment_fqid>/likes/", LikesView.as_view(), name="get_comment_likes"),
    
    # Comments API
    path('api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments/',MultipleCommentsView.as_view(),name='comments_by_serial'),
    path('api/posts/<path:post_fqid>/comments/',MultipleCommentsView.as_view(),name='comments_by_fqid'),
    path('api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/comments/<uuid:comment_serial>/',SingleCommentView.as_view(),name='comment_by_serial'),
    path('api/comments/<path:comment_fqid>/',SingleCommentView.as_view(),name='comment_by_fqid'),

    # Image API
    path('api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/image/', ImageView.as_view(), name="get_image_by_serial"),
    path('api/posts/<path:post_fqid>/image/', ImageView.as_view(), name="get_image_by_fqid"),

    # Posts API
    path("api/authors/<uuid:author_serial>/posts/<uuid:post_serial>/", AuthorPostView.as_view(), name="author_post"),
    path("api/authors/<uuid:author_serial>/posts/", AuthorPostsAllView.as_view(), name="create_post"),
    path("api/authors/<int:author_serial>/posts/", AuthorPostsAllView.as_view(), name="create_post_integer"), # some groups uses int as id
    path("api/posts/<path:post_fqid>/", PostView.as_view(), name="post"),

    # Likes API (specific Likes)
    path("api/authors/<uuid:author_serial>/liked/<uuid:like_serial>/", LikeView.as_view(), name="get_like_by_serial"),
    path("api/liked/<path:like_fqid>/", LikeView.as_view(), name="get_like_by_fqid"),

    # Likes API (Author Likes)
    path("api/authors/<uuid:author_serial>/liked/", AuthorLikesView.as_view(), name="author_likes_by_serial"),
    path("api/authors/<path:author_fqid>/liked/", AuthorLikesView.as_view(), name="author_likes_by_fqid"), 

    # Authors API
    path("api/authors/all/", AuthorsCompleteView.as_view(), name="authors_all"),
    path("api/authors/<uuid:author_serial>/", AuthorsSpecificView.as_view(), name="author_serial"),
    path("api/authors/<path:author_fqid>/", AuthorsSpecificView.as_view(), name="author_fqid"),
    path("api/authors/", AuthorsView.as_view(), name="authors_list"),

    # Share API
    path("api/share/<uuid:author_serial>/", ShareView.as_view(), name="shared"),
    
    # Auth
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path("api/check_auth/", CheckAuthView.as_view(), name="check_auth"),

    # Site and Node Configuration
    path('api/config/', SiteConfigView.as_view(), name='registration_toggle'),
    path('api/nodes/', GetNodesView.as_view(), name="get_nodes"),
    path('api/nodes/add/', AddNodeView.as_view(), name="add_node"),
    path('api/nodes/update/', UpdateNodeView.as_view(), name="edit_node"),
    path('api/nodes/delete/', DeleteNodeView.as_view(), name="remove_node"),

    # Front end injection
    path('', TemplateView.as_view(template_name='index.html')),
]