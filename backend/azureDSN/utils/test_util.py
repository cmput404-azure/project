from django.contrib.contenttypes.models import ContentType
from ..models import *


def create_user():
    user_obj = User.objects.create(display_name="Test User", 
                                    host="http://testserver", 
                                    github="http://github.com/quin",
                                    profile_image="http://testserver.com/image.png",
                                    page="http://testserver/profile")
    return user_obj
    
def create_post(user_obj):        
    post_obj = Post.objects.create(user=user_obj,
                                    title="Test Post",
                                    content="This is a test post",
                                    content_type="text/plain",
                                    visibility=1,
                                    has_image=False,
                                    image=None)
    return post_obj

def create_user_givenID(user_id):
    user_obj = {
        "type": "author",
        "id": f"http://127.0.0.1:8000/authors/{user_id}",
        "url": f"http://127.0.0.1:8000/authors/{user_id}",
        "host": "http://127.0.0.1:8000/",
        "displayName": "Test User",
        "github": "http://github.com/quin",
        "profileImage": "http://testserver/profile"
    }
    return user_obj
    
def create_follow(actor, object):
    follow_obj = FollowRequest.objects.create(object=object, actor=actor)
    return follow_obj


def create_inbox_item(object, inbox_obj):
    content_type = ContentType.objects.get_for_model(object)
    id = getattr(object, 'uuid', getattr(object, 'id', None))
    inbox_item_obj = InboxItem.objects.create(content_type=content_type,
                                                 object_id=id,
                                                 content_object=object)
    inbox_obj.items.add(inbox_item_obj)

    return inbox_item_obj
