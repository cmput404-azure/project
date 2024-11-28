import { Author } from "../models/models";
import { api } from "./config";

interface StreamData {
   author: Author;
   comments: Comment[] | null;
   content: string;
   contentType: string;
   id: string;
   published: string;
   title: string;
   type: string;
   visibility: number;
}

interface PaginatedResponse {
   src: StreamData[];
   page_number: number; // Current page number
   count: number;       // Total number of posts available
   size: number;        // Number of items per page
 }

class StreamService{
   /**
      * Fetch paginated stream from the backend
      * @param auth - if authentication is required
      * @param page - the page number to fetch
      * @param size - the number of items per page
      * @returns paginated stream data
   */
   public async getStream(auth: boolean = false, page: number = 1, size: number = 10): Promise<PaginatedResponse> {
      try {
         const endpoint = auth ? "/api/stream/auth" : "/api/stream/";
         const req = await api.get<PaginatedResponse>(endpoint, {
           params: { page, size },
         });
         return req.data;
       } catch (error) {
         console.error("Error fetching the stream data", error);
         return { src: [], page_number: 1, count: 0, size: 15 };
       }
   }
}


// Create default instance of the service
const stream = new StreamService();
export default stream;