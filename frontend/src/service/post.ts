import { PostData } from "../models/models";
import { api } from "./config"

class PostService {

   /**
    * Fetch a single post by its fully qualified ID (FQID)
    * @param fqid - fully qualified post ID (e.g., "api/posts/{POST_FQID}")
    * @returns Promise<PostData> - the requested post
    */
   public async getPost(fqid: string): Promise<PostData> {
      try {
         let encoded_fqid = encodeURIComponent(fqid);
         const response = await api.get<PostData>(encoded_fqid);
         return response.data;
      } catch (error) {
         console.error(`Error fetching post with ID ${fqid}:`, error);
         throw error;
      }
   }
}

// Create a default instance of the service
const postService = new PostService();
export default postService;