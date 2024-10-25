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

/* 
   Fetch stream from backend
   @param auth: boolean - if authentication is required

   @returns: any - stream data
*/
export async function getStream(auth: boolean = false): Promise<StreamData[]> {
   try {
      if(auth) {
         const req = await api.get<StreamData[]>("/api/stream/auth");
         return req.data;
      }
      const req = await api.get<StreamData[]>("/api/stream/");
      return req.data;
   }
   catch (error) {
      console.error("Error fetching the stream data", error);
      return [];
   }
}

