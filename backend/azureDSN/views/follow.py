from ..utils import url_parser
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from ..serializers import FollowSerializer, UserSerializer
from ..models import Follow, User
from urllib.parse import unquote, urlparse
from requests.auth import HTTPBasicAuth
import requests, os

def fetch_remote_follower_data(remote_url):
    """
    Fetches remote follower data by sending a get request using the remote_url
    """
    try:
        # Parse the remote URL to get the host and remote author uuid
        remote_url = url_parser.percent_decode(remote_url)
        base_host = url_parser.get_base_host(remote_url)
        author_uuid = url_parser.extract_uuid(remote_url)

        remote_api_url = f"{base_host}/api/authors/{author_uuid}/"
        response = requests.get(
            remote_api_url,
            auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD')),
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"Access forbidden to the remote node.")
            return None
        else:
            print(f"Failed to fetch author: {response.text}")
            return None
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
        user = get_object_or_404(User, uuid=user_id)
        # Fetch both local and remote authors that I'm following
        my_followees = Follow.objects.filter(local_follower=user)

        local_followee = []
        remote_followee = []
        for follow in my_followees:
            if follow.local_followee:
                local_followee.append(follow.local_followee)
            elif follow.remote_followee:
                try:
                    remote_user = fetch_remote_follower_data(follow.remote_followee)
                    if remote_user:
                        remote_followee.append(remote_user)
                except Exception as e:
                    print(f"Error fetching remote followee data: {e}")

        local_serializer = UserSerializer(local_followee, many=True)
        response_data = {
            "type": "followers",
            "followers": local_serializer.data + remote_followee,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def get_friends(self, user_id):
        """
        Example call: http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/following/?action=following
        """   
        # Fetch all local and remote followee
        local_followee_ids = set(Follow.objects.filter(local_follower_id=user_id).values_list('local_followee_id', flat=True))
        remote_followee_urls = set(Follow.objects.filter(local_follower_id=user_id).values_list('remote_followee', flat=True))
        
        # Fetch all local and remote follower
        local_follower_ids = set(Follow.objects.filter(local_followee_id=user_id).values_list('local_follower_id', flat=True))
        remote_follower_urls = set(Follow.objects.filter(local_followee_id=user_id).values_list('remote_follower', flat=True))

        # Find mutual relationships (local & remote friends)
        mutual_local_friends = local_followee_ids.intersection(local_follower_ids)
        mutual_remote_friends = remote_followee_urls.intersection(remote_follower_urls)

        local_friends = User.objects.filter(uuid__in=mutual_local_friends)

        remote_friends = []
        # Add remote friends by fetching data from each remote follow URL
        for remote_friend_url in mutual_remote_friends:
            remote_follower_data = fetch_remote_follower_data(remote_friend_url)
            if remote_follower_data:
                remote_friends.append(remote_follower_data)

        local_serializer = UserSerializer(local_friends, many=True)
        return Response(local_serializer.data + remote_friends, status=status.HTTP_200_OK)
    
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
        try:
            # local user
            User.objects.get(uuid=user_id)
            # Get the followers list from Follow model
            followers = Follow.objects.filter(local_followee_id=user_id) 
            local_followers = []
            remote_followers = []
            for follower in followers:
                if follower.remote_follower:  # Remote follower handling
                    remote_data = fetch_remote_follower_data(follower.remote_follower)
                    if remote_data:
                        remote_followers.append(remote_data)
                else:  # Local follower handling
                    try:
                        user = User.objects.get(uuid=follower.local_follower_id)
                        local_followers.append(user)
                    except User.DoesNotExist:
                        return Response({"error": "Local follower not found."}, status=404)

            local_serializer = UserSerializer(local_followers, many=True)

            response_data = {
                "type": "followers",
                "followers": local_serializer.data + remote_followers,
            }
            return Response(response_data, status=200)
            
        except User.DoesNotExist:
            # remote user
            try:
                remote_host = request.GET.get('host')
                if not remote_host:
                    return Response({"message": "Host is required for remote users."}, status=status.HTTP_400_BAD_REQUEST)
                
                remote_host = url_parser.percent_decode(remote_host)
                base_host = url_parser.get_base_host(remote_host)
                
                # send request to fetch all posts
                remote_user_url = f"{base_host}/api/authors/{user_id}/followers"
                response = requests.get(
                    url=remote_user_url,  
                    auth=HTTPBasicAuth(os.getenv('NODE_USERNAME'), os.getenv('NODE_PASSWORD'))
                )
                if response.status_code == 200:
                    # Now, the idea is that the folowers returned by whitesmoke is paginated and we don't need that
                    response_data = response.json()
                    if 'next' in response_data:
                        # Return 'results' if present, else return a followers format response
                        results = response_data.get('results')
                        if results is not None:
                            return Response(results[0], status=status.HTTP_200_OK)
                        else:
                            return Response({'type': 'followers', 'followers': []}, status=status.HTTP_200_OK)
                    else:
                        # If not paginated, return as usual
                        return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": f"Failed to fetch posts from remote host. Status code: {response.status_code}",
                        "details": response.text
                    }, status=status.HTTP_502_BAD_GATEWAY)
            
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
    
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
        Checks if follower_url is a follower of user_id, returns a boolean
        """
        return self.check_follower(request, user_id, follower_url)

    
    
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
        follower_id = url_parser.extract_uuid(decoded_url)
        # remote follower
        follower = Follow.objects.filter(local_follower_id = follower_id, remote_followee__contains=user_id)

        # local follower
        if not follower:
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
        parts = decoded_url.strip("/").split("/")
        follower_host = f"{parts[0]}//{parts[2]}"  
        follower_id = parts[-1]

        try:
            user = User.objects.get(uuid=user_id) # Make sure the user exists
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        follower_local = False
        
        base_url = settings.BASE_URL.rstrip('/api/') # Base means just the scheme, host, port (if exists)

        if follower_host.find(base_url)!=-1:
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
   
        follower = Follow.objects.filter(local_followee_id=user_id, remote_follower__contains=follower_id)

        if follower:
            return Response({"is_follower": True}, status=200) # Remote follower
        else:
            follower = Follow.objects.filter(local_followee_id=user_id, local_follower__uuid=follower_id)
            
            if not follower:
                return Response({"is_follower": False}, status=404) # Neither local nor remote
            else:
                return Response({"is_follower": True},status=200) # Local follower
