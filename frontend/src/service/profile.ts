import { Author, PostData as Post } from "../models/models";

import { AuthorPostsResponse } from "../models/models";
import { api } from "./config";

class ProfileService {
   /**
   *  Fetch author data from backend
   * @param userId: string - the id of the user to fetch
   * @returns: Author - the author data or null if error
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

   /**
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

   /**
      Fetch author posts from backend
      @param userId: string - the id of the user to fetch
      @returns: Post[] - the author posts or null if error
   */
   public async fetchAuthorPosts(userId: string, page: number = 1, size: number = 10, host?: string): Promise<AuthorPostsResponse> {
      try {
         const params: Record<string, any> = {
            page: page,
            size: size,
         };

         // Add `host` only if it is provided
         if (host) {
               params.host = host;
         }
         const response = await api.get<AuthorPostsResponse>(`/api/authors/${userId}/posts/`, {
            params,
         });

         return {
            count: response.data.count,
            src: response.data.src,
            page_number: response.data.page_number,
            size: response.data.size,
            type: response.data.type,
         };
      } catch (error) {
         console.error("Error fetching the author posts", error);
         return {
            count: 0,
            src: [],
            page_number: 1,
            size: 10,
            type: "posts",
         };
      }
   }

   /**
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

   /**
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

   /**  
        Fetch all the local users of the current users
        @param: uuid: uuid of the current user, might be anonymous
        @returns User[]: list of users
   */
   public async fetchAllAuthors(): Promise<Author[]> {
      try {
         const response = await api.get<any>(`/api/authors/`);
         return (response.status === 200) ? response.data.authors : []; 
      } catch (error) {
         console.error('Error fetching authors:', error);
         return []; 
      }
   }

   /** 
      Fetch the list of recommended authors from remote node
      @returns Promise<Author[]> - List of recommended authors 
   */
   public async fetchRecommendedAuthors(): Promise<Author[]> {
      try {
         const response = await api.get<{ recommended_authors: Author[] }>(`/api/authors/recommended/`);
         return response.status === 200 ? response.data.recommended_authors : [];
      } catch (error) {
         console.error('Error fetching recommended authors:', error);
         return [];
      }
   }

   /**
      Generates the profile picture if no profile picture is provided
      @param author: Author - the author data
      @returns string - the profile picture url
   */
   public getProfilePicture(author: Author, initial?: boolean): string {
      if (initial || !author.profileImage) {
         return `https://ui-avatars.com/api/?background=random&name=${author.displayName}`;
      }
      return author.profileImage;
   }
}

const profileService = new ProfileService();
export default profileService;