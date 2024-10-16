from django.urls import path
from .viewFolder.views_follower import get_followers, add_follower


# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    # path("/api/authors/<uuid:user_id>/inbox/", InboxView.as_view(), name="inbox")
    path('service/api/authors/<uuid:user_id>/followers/', get_followers, name='followers'),
    path('service/api/authors/<user_id>/followers/<follower_id>/add/', add_follower, name='add_follower'),

    # path('/api/authors/{user_id}/followers/{follower_id}', 
    # path('follow/<int:pk>/', FollowDetailView.as_view(), name='follow-detail'),
]
