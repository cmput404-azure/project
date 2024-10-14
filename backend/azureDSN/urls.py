from django.urls import path
from .views import *

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path("/api/authors/<uuid:user_id>/inbox/", InboxView.as_view(), name="inbox")
]
