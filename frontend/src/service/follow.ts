import { Follower } from "../models/models";
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
   public async getFollowers(uuid: string): Promise<Follower[]> {
      try {
         const response = await api.get<FollowerResponse>(`/api/authors/${uuid}/followers/`, {
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
}

// Create default instance of the service
const follow = new FollowService();
export default follow;