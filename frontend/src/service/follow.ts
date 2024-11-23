import { Follower, Author, User } from "../models/models";
import { api } from "./config";

export interface FollowerResponse {
   followers: Follower[];
}

class FollowService{
   /* 
      Gets the friends of the user
      @param uuid: string - the uuid of the user
      @returns: Follower[] - the list of friends
   */
   public async getFriends(uuid: string): Promise<Follower[]> {
      try {
         const response = await api.get<Follower[]>(`/api/authors/${uuid}/following/`, {
            params: {
               action: 'friends'
            }
         });
         return response.data;
      } 
      catch (error) {
         console.error('Fetch friends error:', error);
         return [];
      }
   }

   /* 
      Gets the followers of the user
      @param uuid: string - the uuid of the user
      @returns: Follower[] - the list of followers
   */
   public async getFollowers(uuid: string, host?: string): Promise<Follower[]> {
      try {
         const params: Record<string, string> = {};
         if (host) {
               params.host = host; // Add host only if provided
         }
        
         const response = await api.get<FollowerResponse>(`/api/authors/${uuid}/followers/`, {
            params: params,
         });

         /* 
            Note for future creation of service layer api handlers:

            Return the followers array directly instead of a follower response since we already know
            the response structure, then this is handled in the service layer
            with the correct logic and responses.

            ex. if the response has {type:"followers", followers: []} 
               then can just return followers directly, 
               react does not need to know.
         */
         return response.data.followers;
      } 
      catch (error) {
         console.error('Fetch followers error:', error);
         return [];
      }
   }

   /* 
      Gets the users that the user is following
      @param uuid: string - the uuid of the user
      @returns: Follower[] - the list of following
   */
   public async getFollowing(uuid: string): Promise<Follower[]> {
      try {
         const response = await api.get<FollowerResponse>(`/api/authors/${uuid}/following/`, {
            params: {
               action: 'following'
            }
         });
         return response.data.followers;
      } 
      catch (error) {
         console.error('Fetch following error:', error);
         return [];
      }
   }

   public async checkFollowing(uuid: string, follower_url:string): Promise<boolean> {
      try {
         const response = await api.get<{ is_follower: boolean }>(`/api/authors/${uuid}/followers/${follower_url}/`);
         return response.data.is_follower;;
      } 
      catch (error) {
         if (error.response.status !== 404) {
            console.error('Fetch following error:', error);
        }
         return false;
      }
   }

   public async unfollow(userId:string, follower:User){
      //follower is the logged in user, user is the user profile we're viewing
      const userResponse = await api.get<Author>(`/api/authors/${follower.uuid}/`);
      const encodedUrl = encodeURIComponent(userResponse.data.id);

      if (userId.includes('/')) {
         // Split the URL by '/' and take the last part as the ID
         userId = userId.replace(/\/+$/, '').split('/').pop() || userId;
     }
 
      try {
         await api.delete(`/api/authors/${userId}/followers/${encodedUrl}/`);
      } catch (error) {
         console.error('Fetch error:', error);
      }
   }

   public async addFollower(userId:string, follower_url:string){ 
      try {
         await api.put(`/api/authors/${userId}/followers/${follower_url}/`);
      } catch (error) {
         console.error('Fetch error:', error);
      }
   }
}

// Create default instance of the service
const follow = new FollowService();
export default follow;