from django.urls import path
from . import views
from .view import *

# urlpatterns contains all of the routes that this application supports routing for.
# this routes traffic from polls/ to the index function that we defined earlier in the views file.
urlpatterns = [
    path("", views.index, name="index"),
    path("/api/authors/<uuid:user_id>/inbox/", InboxView.as_view(), name="inbox")
]
