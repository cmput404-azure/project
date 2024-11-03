import json
from uuid import UUID
from django.http import Http404
from rest_framework.views import APIView
import http.client
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.utils import inline_serializer
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from django.conf import settings
from ..serializers.follow_serializer import FollowSerializer
from ..serializers.user_serializer import UserSerializer
from ..models import Follow
from ..models import User
from urllib.parse import quote, unquote, urlparse
from django.db.models import Q

def fetch_remote_follower_data(remote_url):
    """
    Fetches remote follower data by sending a get request using the remote_url
    """
    try:
        # Parse the remote URL to get the host and path
        parsed_url = urlparse(remote_url)

        if not parsed_url.path.endswith('/'):
            parsed_url = parsed_url._replace(path=parsed_url.path + '/')
        connection = http.client.HTTPConnection(parsed_url.netloc)

        # Perform the GET request
        connection.request("GET", parsed_url.path)
        response = connection.getresponse()
        data = json.loads(response.read().decode())       
        parts = data.get("id").strip("/").split("/")

        userData={ 
            "id": parts[-1],
            "host": data.get("host"),
            "displayName": data.get("displayName"),
            "username": data.get("username"),
            "bio":data.get("bio"),
            "github": data.get("github"),
            "profile_image": data.get("profileImage"),
            "page": data.get("page")
            }
        serializer = UserSerializer(data = userData)
        if serializer.is_valid():
            user = User(**serializer.validated_data)  # Create an unsaved User instance
            return user
        else:
            print("Errors:", serializer.errors)
        
    except Exception as e:
        print(f"Error fetching remote follower {remote_url}: {str(e)}")
        return None
        
class FollowCustomView(APIView):
    @extend_schema(
        summary="Retrieve following users or friends based on query parameters",
        description="""
            This endpoint retrieves a list of users the specified user is following 
            or their mutual friends based on the provided `action` query parameter.

            action=following: Returns the list of users the given user is following.
            action=friends: Returns the list of mutual followers (friends).
        """,
        operation_id='get_following_or_friends',
        parameters=[
            OpenApiParameter(
                name='user_id',
                description='UUID of the user to retrieve data for.',
                type=str,
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='action',
                description='Specifies the operation to perform.',
                type=str,
                required=True,
                location=OpenApiParameter.QUERY
            )
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="FollowingFriendsResponse",
                    fields={
                        'type': serializers.CharField(),
                        'followers': FollowSerializer(many=True),
                    }
                ),
                description='List of users retrieved successfully based on the action parameter.'
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='The specified user was not found.'
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Invalid action parameter or other bad request.'
            ),
        }
    )
    def get(self, request, user_id):
        """
            Based on query parameters following or friends, will direct to either get the 
            users that current user is following or get the list of friends
            Both actions will return User objects
        """
        action = request.query_params.get('action')

        if action =='following':
            return self.get_following(user_id)
        elif action == 'friends':
            return self.get_friends(user_id)
    
    def get_following(self, user_id):
        """
        Example call: http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/following/?action=following
        """
        # Get all the users where user is the follower
        local_followers = Follow.objects.filter(local_follower_id = user_id)
        remote_followers = Follow.objects.filter(remote_follower__contains=f"/{user_id}")
        userList = []
        all_followers = list(local_followers) + list(remote_followers)

        #  combined_followers = []
        # for follower in followers:
        #     if follower.remote_follower:  # Remote follower handling
        #         remote_data = fetch_remote_follower_data(follower.remote_follower)
        #         if remote_data:
        #             combined_followers.append(remote_data)
        #     else:  # Local follower handling
        #         try:
        #             user = User.objects.get(uuid=follower.local_follower_id)
        #             combined_followers.append(user)
        #         except User.DoesNotExist:
        #             raise Http404(f"Local follower with ID {follower.local_followee_id} not found.")


        for follower in all_followers:
            try:
                user = User.objects.get(uuid=follower.local_followee_id)
                userList.append(user)
            except User.DoesNotExist:
                raise Http404(f"Local follower with ID {follower.local_followee_id} not found.")
        
        serializer = UserSerializer(userList, many=True)
        response_data = {
                "type": "followers",
                "followers": serializer.data,
                }
        return Response(response_data)
    
    def get_friends(self, user_id):
        """
        Example call: http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/following/?action=following
        """
        # get ids that user_id follows
        # followee_ids = Follow.objects.filter(local_follower_id=user_id).values_list('local_followee_id', flat=True)
        # remote_followee_ids = Follow.objects.filter(remote_follower__contains = user_id).values_list('local_followee_id', flat = True)
        
       # Get followee_ids of users that user_id follows
        followee_ids = list(Follow.objects.filter(local_follower_id=user_id).values_list('local_followee_id', flat=True))

        # Get remote followee_ids that are in the remote followers URLs
        remote_followee_ids = list(Follow.objects.filter(remote_follower__contains=user_id).values_list('local_followee_id', flat=True))

        # Combine both lists of followees
        all_followee_ids = set(followee_ids) | set(remote_followee_ids)  # Using set to ensure uniqueness
        
        # Build the Q object for the remote follower check
        remote_follower_q = Q()  # Start with an empty Q object

        # Dynamically create Q objects for each followee ID to check if it is at the end of the remote_follower URLs
        for followee_id in all_followee_ids:
            remote_follower_q |= Q(remote_follower__endswith=f"/{followee_id}")  # Check if the remote_follower URL ends with the followee_id

        # Now query mutual followers considering both local and remote
        if remote_follower_q:
            mutual_followers = Follow.objects.filter(
                (Q(local_followee_id=user_id) & Q(local_follower_id__in=all_followee_ids)) | 
                (remote_follower_q & Q(local_followee_id=user_id))
            )
        else:
            mutual_followers = Follow.objects.filter(
                Q(local_followee_id=user_id) & Q(local_follower_id__in=all_followee_ids)
            )
        combined_friends = []

        # Get the list of friend ids
        local_friend_ids = mutual_followers.values_list('local_follower_id', flat=True)

        remote_friend_ids = mutual_followers.values_list('remote_follower', flat = True)
        # remote
        for remote_friend in remote_friend_ids:
            remote_follower_data = fetch_remote_follower_data(remote_friend)
            if remote_follower_data:  # Ensure the data is not None or empty
                combined_friends.append(remote_follower_data)

        # Local users
        local_friends = User.objects.filter(uuid__in=local_friend_ids)
        combined_friends.extend(local_friends)

        serializer = UserSerializer(combined_friends, many=True)
        return Response(serializer.data)
    
class FollowerView(APIView):
    @extend_schema(
        summary="Get all the followers of the user",
        description="""
            Returns both remote and local followers of the user
        """,
        operation_id="followers",
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="UUID of the user",
                type=str,
                location=OpenApiParameter.PATH,
                required=True

            ),
            OpenApiParameter(
                name="follower_url",
                description="URL of the follower",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(response=UserSerializer,description="Followers retrieved successfully"),
            404: OpenApiResponse(description="The follower does not exist")
        }
    )
    def get(self, request, user_id):
        """
        Get all the followers of a local user

        """
        # Get the followers list from Follow model
        followers = Follow.objects.filter(local_followee_id=user_id) 
        combined_followers = []
        for follower in followers:
            if follower.remote_follower:  # Remote follower handling
                remote_data = fetch_remote_follower_data(follower.remote_follower)
                if remote_data:
                    combined_followers.append(remote_data)
            else:  # Local follower handling
                try:
                    user = User.objects.get(uuid=follower.local_follower_id)
                    combined_followers.append(user)
                except User.DoesNotExist:
                    raise Http404(f"Local follower with ID {follower.local_followee_id} not found.")

        # Using the remote_follower_id and local_follower_id, use the GET user endpoint

        serializer = UserSerializer(combined_followers, many=True)
        response_data = {
        "type": "followers",
        "followers": serializer.data,
        }
        return Response(response_data, status=200)
    
class FollowView(APIView):        
    http_method_names = ['get', 'put', 'delete'] 

    @extend_schema(
        summary="Checks follower relationship",
        description="""
            Checks if the follower_url is a follower of user_id
        """,
        operation_id="follower_changes",
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="UUID of the user",
                type=str,
                location=OpenApiParameter.PATH,
                required=True

            ),
            OpenApiParameter(
                name="follower_url",
                description="URL of the follower",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(description="Is a follower"),
            404: OpenApiResponse(description="Not a follower")
        }
    )
    def get(self, request, user_id, follower_url=None):
        """
        Directs get request to either check for a follow relationship or to get list of all followers 
        """

        # Check if the user_id and follower_url should perform the "check follower" logic
        if follower_url:
            return self.check_follower(request, user_id, follower_url)

        # If no follower_url is provided, handle another GET operation
        return self.get_followers(request, user_id)
    
    
    @extend_schema(
        summary="Adds a follower to the user",
        description="""
            Adds a follower to the database, determining if the follower is local or remote
        """,
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="UUID of the user",
                type=str,
                location=OpenApiParameter.PATH,
                required=True

            ),
            OpenApiParameter(
                name="follower_url",
                description="URL of the follower",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(description="Follower added successfully"),
            409: OpenApiResponse(description= "Follower is already following user"),
            404: OpenApiResponse(description="Error when adding follower")
        }
    )
    def put(self, request, user_id, follower_url):
        """Adds follower to the user"""
        return self.add_follower(request, user_id, follower_url)

    @extend_schema(
        summary="Deletes follower",
        description="""
            Removes the follow relationship in the database
        """,
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="UUID of the user",
                type=str,
                location=OpenApiParameter.PATH,
                required=True

            ),
            OpenApiParameter(
                name="follower_url",
                description="URL of the follower",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(description="Follower removed successfully"),
            404: OpenApiResponse(description="Follower not found"),
        }
    )
    def delete(self, request, user_id, follower_url):
        """Removes follower from user"""
        return self.remove_follower(request, user_id, follower_url)

    def remove_follower(self, request, user_id, follower_url):
        """
        Deletes the follow entry so that user is no longer following follower
        """
        decoded_url = unquote(follower_url)
        # remote follower
        follower = Follow.objects.filter(local_followee_id = user_id, remote_follower__contains=decoded_url)

        # local follower
        if not follower:
            parts = decoded_url.strip("/").split("/")
            follower_id = parts[-1]
            follower = Follow.objects.filter(local_followee_id = user_id, local_follower_id=follower_id)
        else:
            follower.delete()
            return Response({"message":"Follower removed successfully"}, status = 200)
        
        # Verifies that follower exists
        if not follower:
            return Response({"error": "Follower not found"}, status=404)
    
        follower.delete()
        return Response({"message": "Follower removed successfully"}, status=200)

    def add_follower(self,request, user_id, follower_url):  

        # Get the necessary information from follower_url
        decoded_url = unquote(follower_url)
        print(decoded_url)
        parts = decoded_url.strip("/").split("/")
        follower_host = f"{parts[0]}//{parts[2]}"  
        follower_id = parts[-1]

        try:
            user = User.objects.get(uuid=user_id) # Make sure the user exists
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        follower_local = False
        if follower_host.find(settings.BASE_URL)!=-1:
            follower_local = True

        # Check if this follow relationship already exists
        existing_follow = Follow.objects.filter(
            local_followee=user if follower_local else None,
            remote_followee=None,
            local_follower=follower_id if follower_local else None,
            remote_follower=None if follower_local else decoded_url
        ).exists()

        if existing_follow:
            return Response({"message": "Already following"}, status=409)
        
        # Insert data as normal if the relationship doesn't already exist

        follow_data = {
            "local_followee": user_id,
            "remote_followee": None,
            "local_follower": follower_id if follower_local else None,
            "remote_follower": decoded_url if not follower_local else None,
        }
        serializer = FollowSerializer(data=follow_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Follower added successfully"}, status=200)
        else:
            return Response(serializer.errors, status=400)

    def check_follower(self,request, user_id, follower_url):
        """
        Checks if the second id is a follower of the first id
        Example call: http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/followers/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2F337f58f8-5811-4213-8311-1c7dc8e6038d/
        
        """
        # remote follower
        decoded_url = unquote(follower_url)
        parts = decoded_url.strip("/").split("/")
        follower_id = parts[-1]
   
        follower = Follow.objects.filter(local_followee_id = user_id, remote_follower__contains=follower_id)

        # local follower
        if not follower:
            decoded_url = unquote(follower_url)
            parts = decoded_url.strip("/").split("/")
            follower_id = parts[-1]
            follower = Follow.objects.filter(local_followee_id = user_id, local_follower_id=follower_id)
        else:
            return Response({"is_follower": True}, status=200)
        if not follower:  # neither local nor remote
            return Response({"is_follower": False}, status=200)
        else:
            return Response({"is_follower": True},status=200)