import { Like, PaginatedLikesResponse } from "../models/models";
import { extractUUID } from "../util/formatting/extractUUID";
import { api } from "./config";

class LikeService {
    /**
    * Fetch a single Like by its Fully Qualified ID (FQID)
    * @param fqid - Fully Qualified Like ID (e.g., "api/liked/{LIKE_FQID}")
    * @returns Promise<Like> - The requested Like object
    */
   public async getLikeByFQID(fqid: string): Promise<Like> {
        try {
            const response = await api.get<Like>(`/api/liked/${fqid}`);
            return response.data;
        } catch (error: any) {
            console.error(`Error fetching like with FQID ${fqid}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
        * Fetch a single Like by Author Serial and Like Serial
        * @param authorSerial - UUID of the Author of the Like
        * @param likeSerial - UUID of the Like
        * @returns Promise<Like> - The requested Like object
        */
    public async getLikeByAuthorAndSerial(authorSerial: string, likeSerial: string): Promise<Like> {
        try {
            const response = await api.get<Like>(`/api/authors/${authorSerial}/liked/${likeSerial}`);
            return response.data;
        } catch (error: any) {
            console.error(`Error fetching like with Author Serial ${authorSerial} and Like Serial ${likeSerial}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
    * Fetch Likes by Author using either authorSerial or authorFQID
    * @param authorSerial - Optional UUID of the Author whose Likes to retrieve
    * @param authorFQID - Optional FQID of the Author whose Likes to retrieve
    * @returns Promise<PaginatedLikesResponse> - The full paginated response object with metadata
    */
    public async getLikesByAuthor(authorSerial?: string, authorFQID?: string): Promise<PaginatedLikesResponse> {
        try {
            let url = "/api/authors/";

            if (authorSerial) {
                url += `${authorSerial}/likes`;
            } else if (authorFQID) {
                url += `${authorFQID}/likes`;
            } else {
                throw new Error("Either authorSerial or authorFQID must be provided.");
            }

            const response = await api.get<PaginatedLikesResponse>(url);
            return response.data;
        } catch (error: any) {
            console.error(`Error fetching likes for author ${authorSerial || authorFQID}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
    * Fetch Likes for posts or comments based on provided parameters
    * @param authorSerial - UUID of the Author of the post or comment
    * @param postSerial - UUID of the Post being liked
    * @param postFQID - Fully Qualified ID of the Post
    * @param commentSerial - UUID of the Comment being liked
    * @returns Promise<PaginatedLikesResponse> - The full paginated response object with metadata
    */
    public async getLikes(authorSerial?: string, postSerial?: string, postFQID?: string, commentSerial?: string): Promise<PaginatedLikesResponse> {
        try {
            let url = "/api/";
            let authorFQID = null;

            if (authorSerial && authorSerial.startsWith("http")) {
                authorFQID = authorSerial;
                authorSerial = extractUUID(authorSerial);
            }

            if (authorSerial && postSerial && commentSerial) {
                url += `authors/${authorSerial}/posts/${postSerial}/comments/${commentSerial}/likes`;
            } else if (authorSerial && postSerial) {
                url += `authors/${authorSerial}/posts/${postSerial}/likes`;
            } else if (postFQID) {
                url += `posts/${postFQID}/likes`;
            } else {
                throw new Error("Invalid parameters: please provide authorSerial and postSerial, or postFQID, or all parameters.");
            }

            if (authorFQID) {
                url += `?authorId=${encodeURIComponent(authorFQID)}`;
            }
            
            const response = await api.get<PaginatedLikesResponse>(url);
            return response.data;
        } catch (error: any) {
            console.error("Error fetching likes:", error.response?.data || error.message);
            throw error;
        }
    }

}

const likeService = new LikeService();
export default likeService;