import { Author, Post } from "../models/models";

import { AuthorPostsResponse } from "../models/models";
import { api } from "./config";

class ProfileService {
   /* 
      Fetch author data from backend
      @param userId: string - the id of the user to fetch
      @returns: Author - the author data or null if error
   */
   public async fetchAuthorData(userId: string): Promise<Author | null> {
      try {
         const response = await api.get<Author>(`/api/authors/${userId}/`);
         return response.data;
      } catch (error) {
         console.error("Error fetching the author data", error);
         return null;
      }
   }

   /*
      Update user info
      @param userId: string - the id of the user to update
      @param data: Author - the data to update
      @returns: void
   */
   public async updateUserInfo(userId: string, data: Author): Promise<void> {
      try {
         await api.put(`/api/authors/${userId}/`, data);
         console.log("User info updated successfully");
      } catch (error) {
         console.error("Error updating user info", error);
      }
   }

   /*
      Fetch author posts from backend
      @param userId: string - the id of the user to fetch
      @returns: Post[] - the author posts or null if error
   */
   public async fetchAuthorPosts(userId: string): Promise<Post[]> {
      try {
         const response = await api.get<AuthorPostsResponse>(`/api/authors/${userId}/posts/`);
         return response.data.results.reverse();
      } catch (error) {
         console.error("Error fetching the author posts", error);
         return [];
      }
   }

   /* 
      Delete a specific post
      @param userId: string - the id of the user to delete post from
      @param postId: string - the id of the post to delete
      @returns: void
   */
   public async deletePost(userId: string, postId: string): Promise<void> {
      try {
         await api.delete(`/api/authors/${userId}/posts/${postId}/`);
         console.log("Post deleted successfully");
      } catch (error) {
         console.error("Error deleting post", error);
      }
   }

   /*
      Update a specific post
      @param userId: string - the id of the user to update post from
      @param postId: string - the id of the post to update
      @param updatedPost: Post - the updated post data
      @returns: void
   */
   public async updatePost(userId: string, postId: string, updatedPost: Post): Promise<void> {
      try {
         await api.put(`/api/authors/${userId}/posts/${postId}/`, updatedPost);
         console.log("Post updated successfully");
      } catch (error) {
         console.error("Error updating post", error);
      }
   }
}

const profileService = new ProfileService();
export default profileService;