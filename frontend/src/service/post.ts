import { PostComment, PostData } from "../models/models";
import { api } from "./config"

class PostService {
   /**
    * Fetch a single post by its fully qualified ID (FQID)
    * @param fqid - fully qualified post ID (e.g., "api/posts/{POST_FQID}")
    * @returns Promise<PostData> - the requested post
    */
   public async getPost(fqid: string): Promise<PostData> {
      try {
         const response = await api.get<PostData>(fqid);
         return response.data;
      } catch (error) {
         console.error(`Error fetching post with ID ${fqid}:`, error);
         throw error;
      }
   }

   /**
     * Fetch comments for a specific post
     * @param postId - The ID of the post
     * @returns Promise<PostComment> - The comments for the post
   */
   public async getPostComments(postId: string): Promise<PostComment> {
      try {
            const encodedId = encodeURIComponent(postId);
            const response = await api.get<PostComment>(`/api/posts/${encodedId}/comments/`);
            return response.data;
      } catch (error) {
            console.error(`Error fetching comments for post with ID ${postId}:`, error);
            throw error;
      }
   }
}

// Create a default instance of the service
const postService = new PostService();
export default postService;