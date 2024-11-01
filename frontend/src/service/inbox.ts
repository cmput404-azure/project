import { Inbox, InboxItem } from "../models/models";
import { api } from "./config";

class InboxService{
    /* 
        Get all the inbox items of the user (including posts, follow requests, comments and likes)
        @param uuid: string - the uuid of the user
        @returns: InboxItem[] - inbox type
    */
    public async getInbox(uuid: string): Promise<InboxItem[]> {
        try {
            const response = await api.get<Inbox>(`/api/authors/${uuid}/inbox/`);
            return response.data.items;
        } 
        catch (error) {
            console.error('Fetch inbox error:', error);
            return [];
        }
    }

    /* 
        Update the post in inbox
        @param uuid: string - the uuid of the user
               post_id: string - the fqid of the post
               title: string - the new title of the post
               content: string - the new content of the post
               visibility: number - the new status of the post  
        @returns: message: string 
    */
    public async updateInboxPost(
        uuid: string,
        post_id: string,
        title: string,
        content: string,
        visibility: number
    ): Promise<string> {
        try {
            post_id = post_id.split('/').pop()
            const response = await api.put<{ message: string }>(`/api/authors/${uuid}/inbox/`, {
                id: post_id,
                title,
                content,
                visibility,
            });
          
            return response.data.message;
        } catch (error) {
            console.error("Update post in inbox error:", error);
            return "";
        }
    }

    /* 
        Delete the inbox of the users
        @param uuid: string - the uuid of the user 
               post_id: string - the fqid of the post
        @returns: message: string
    */
    public async deleteInboxPost(uuid: string, post_id: string): Promise<string> {
        try {
            post_id = post_id.split('/').pop()
            const config = {
                headers: {},
                data: {
                    id: `/api/authors/${uuid}/posts/${post_id}`,
                    type: "post",
                },
            };
          
            const response = await api.delete<{ message: string }>(`/api/authors/${uuid}/inbox/`, config);
          
            return response.data.message;
        } catch (error) {
            console.error("Delete post in inbox error:", error);
            return "";
        }
    }


    /* 
        Delete the inbox of the users
        @param uuid: string - the uuid of the user 
               id: string - follow request id
        @returns: items: InboxItem[] - list of inbox items remaining in the user's inbox
    */
    public async deleteInboxFollowRequest(uuid: string, id: string): Promise<InboxItem[]> {
        try {
            const config = {
                headers: {},
                data: {
                    id: id,
                    type: "follow",
                },
            };
            const response = await api.delete<Inbox>(`/api/authors/${uuid}/inbox/`, config);
            return response.data.items;
        } catch (error) {
            console.error("Delete post in inbox error:", error);
            return [];
        }
    }

    /* 
    Send a inbox item to the inbox of a user
    @param uuid: string - the uuid of the user
           inbox_item: object - the inbox item to be sent
    @returns: message: string 
    */
    public async sendPostToInbox(uuid: string, inbox_item: object): Promise<string> {
        try {
            const inboxResponse = await api.post<{ message: string }>(`/api/authors/${uuid}/inbox/`, inbox_item);
            return inboxResponse.data.message;
        } catch (error) {
            console.error(`Error sending object to inbox of ${uuid}:`, error);
            return "Error";
        }
    }
}

// Create default instance of the service
const inbox = new InboxService();
export default inbox;
