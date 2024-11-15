// import { Author } from "../models/models";
// import { basicAuthApi } from "./config";

// interface PaginatedAuthorResponse {
//     type: string;
//     authors: Author[];
// }

class AuthorService {
    // public async getNodeAuthors(nodeURL: string, username: string, password: string, page: number, size: number) {
    //     try {
    //         // Basic Authentication
    //         const credentials = btoa(`${username}:${password}`);
    //         const headers = {
    //             'Authorization': `Basic ${credentials}`,
    //         };

    //         const req = await basicAuthApi.get<PaginatedAuthorResponse>(`${nodeURL}authors?page=${page}&size=${size}`, {
    //             headers
    //         });
    //         return req.data.authors;
    //     } catch (error) {
    //         console.error("Failed to fetch node authors: ", error);
    //         return [];
    //     }
    // }
}

const author = new AuthorService();
export default author;

  