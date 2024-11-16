import { Author } from "../models/models";
import { api } from "./config";

class UserService{
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
}

// Create default instance of the service
const userService = new UserService();
export default userService;