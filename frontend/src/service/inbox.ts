import { Inbox, InboxItem, PostData } from "../models/models";

import { api } from "./config";
import { extractUUID } from "../util/formatting/extractUUID";

class InboxService {
  /* 
        Get all the inbox items of the user (including posts, follow requests, comments and likes)
        @param uuid: string - the uuid of the user
        @returns: InboxItem[] - inbox type
    */
  public async getInbox(uuid: string): Promise<InboxItem[]> {
    try {
      const response = await api.get<Inbox>(`/api/authors/${uuid}/inbox/`);
      return response.data.items;
    } catch (error) {
      console.error("Fetch inbox error:", error);
      return [];
    }
  }

  public async getInboxPaginated(
    uuid: string,
    page: number,
    size: number
  ): Promise<InboxItem[]> {
    console.log("Fetching inbox paginated");
    console.log("UUID: ", uuid);
    console.log("Page: ", page);
    console.log("Size: ", size);
    try {
      const response = await api.get<Inbox>(
        `/api/authors/${uuid}/inbox/paginated/?page=${page}&size=${size}`
      );
      return response.data.items;
    } catch (error) {
      console.error("Fetch inbox error:", error);
      return [];
    }
  }

  /* 
        Update the post in inbox
        @param uuid: string - the fqid of the user
                post_id: string - the fqid of the post
                title: string - the new title of the post
                content: string - the new content of the post
                visibility: number - the new status of the post  
    */
  public async updateInboxPost(uuid: string, post_obj: any): Promise<string> {
    try {
      uuid = extractUUID(uuid);
      const response = await api.put<{ message: string }>(
        `/api/authors/${uuid}/inbox/`,
        post_obj
      );

      return response.data.message;
    } catch (error) {
      console.error("Update post in inbox error:", error);
      return "";
    }
  }

  /* 
        Delete the inbox of the users
        @param uuid: string - the uuid of the user 
               post_obj: Post - the deleted post object
        @returns: message: string
    */
  public async deleteInboxPost(uuid: string, post_obj: any): Promise<string> {
    try {
      uuid = extractUUID(uuid);
      const config = {
        headers: {},
        data: post_obj,
      };

      const response = await api.delete<{ message: string }>(
        `/api/authors/${uuid}/inbox/`,
        config
      );
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
  public async deleteInboxFollowRequest(
    uuid: string,
    id: string
  ): Promise<InboxItem[]> {
    try {
      const config = {
        headers: {},
        data: {
          id: id,
          type: "follow",
        },
      };
      const response = await api.delete<Inbox>(
        `/api/authors/${uuid}/inbox/`,
        config
      );
      return response.data.items;
    } catch (error) {
      console.error("Delete post in inbox error:", error);
      return [];
    }
  }

  /* 
    Send a inbox item to the inbox of a user
    @param uuid: string - the fqid of the user
           inbox_item: object - the inbox item to be sent
    @returns: status
    */
  public async sendPostToInbox(fqid: string, inbox_item: object): Promise<any> {
    const uuid = extractUUID(fqid);
    try {
      const inboxResponse = await api.post<any>(
        `/api/authors/${uuid}/inbox/`,
        inbox_item
      );
      return inboxResponse.status;
    } catch (error) {
      console.error(`Error sending object to inbox of ${fqid}:`, error);
      return "Error";
    }
  }

  /* 
    Send a comment into the inbox of a user
    @param uuid: string - the fqid of the user
           inbox_item: object - the inbox item to be sent
    @returns: message: string 
    */
  public async sendCommentToInbox(
    uuid: string,
    inbox_item: object
  ): Promise<Comment | null> {
    uuid = extractUUID(uuid);
    try {
      const inboxResponse = await api.post<Comment>(
        `/api/authors/${uuid}/inbox/`,
        inbox_item
      );
      return inboxResponse.data;
    } catch (error) {
      console.error(`Error sending object to inbox of ${uuid}:`, error);
      return null;
    }
  }
}

// Create default instance of the service
const inbox = new InboxService();
export default inbox;
