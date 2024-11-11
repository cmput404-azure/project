import { Share } from "../models/models";
import { api } from "./config";

class ShareService{
    /* 
        Check whether that user has shared that post
        @param post_fqid: fqid of the post
               uuid: uuid of the person we want to check 
        @returns: boolean - true indicate shared, false otherwise
    */
    public async checkShare(post_fqid: string, uuid: string): Promise<boolean> {
        try {
            // Using GET request and passing post_fqid as a query parameter
            const response = await api.get<{ exists: boolean }>(`/api/share/${uuid}/`, {
                params: { post_fqid }
            });
            return response.data.exists;
        } 
        catch (error) {
            console.error('Check share error:', error);
            return false;
        }
    }


    /* 
        Add share into share model
        @param payload: contains fqid of the post
               uuid: uuid of the person we want to check 
        @returns: message: string
    */
    public async addShare(payload: Share, uuid: string): Promise<string> {
        try {
            const response = await api.post<{ message: string }>(`/api/share/${uuid}/`, payload);
            return response.data.message; 
        } 
        catch (error) {
            console.error('Check share error:', error);
            return null;
        }
    }
}

// Create default instance of the service
const share = new ShareService();
export default share;