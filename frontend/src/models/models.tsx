import {ContentType} from "./modelTypes"

export interface Author {
    type: string;
    id: string;
    host: string;
    displayName: string;
    username: string;
    bio?: string | null;
    github?: string | null;
    profileImage?: string | null;
    page: string;
}

export interface User{
    host: string;
    username: string;
    uuid: string;
    profileImage: string | null;
    is_staff: boolean;
}

export interface FollowRequest {
    type: string;
    summary: string;
    actor: {
        type: string;
        id: string;
        host: string;
        displayName: string;
        github: string;
        profileImage: string;
        page: string;
    }
    object: Author
}

export interface Follower {
    displayName: string;
    github: string;
    host: string;
    id: string; // use the host and id to get the foreign fqid
    page: string;
    type: string;
    profileImage?: string | null;
}
export interface Like {
    type: string;
    author: Author;
    published: string;
    id: string;
    object: string;
}

export interface Comment {
    type: string;
    author: Author;
    comment: string;
    contentType: ContentType;
    published: string;
    id: string;
    post: string;
}

export interface PostData {
    type?: string | "post";
    title: string;
    id: string;
    contentType: string;
    content: string;
    description: string;
    author: Author;
    comments: PostComment;
    likes: PaginatedLikesResponse;
    published: string;
    modified_at:string;
    visibility: string;
    shared_by?: string; // only for share functionality
}

export interface PaginatedLikesResponse {
    type: string;
    id: string;
    page: string;
    page_number: number;
    size: number;
    count: number;
    src: Like[];
}

export interface PostComment {
    type: string;
    id: string;
    page: string;
    page_number: number;
    size: number;
    count: number;
    src: Comment[];
}

// This might be one of the four: post, like, comment and request so I simply store all the possible variables
export interface InboxItem {
    type: string;
    id: string;
    title?: string;
    description?: string;
    author?: Author;
    contentType?: ContentType;
    comments?: Comment[];
    likes?: Like[];
    published?: string;
    visibility?: number;
    comment?: string;
    post?: string;
    object?: string | Author;
    summary?: string;
    actor?: Author;
}

export interface Inbox {
    user: string;
    type: string;
    items: InboxItem[]
}

export interface AuthorPostsResponse {
    type: string;
    count: number;
    src: PostData[];
    page_number: number;
    size: number;
}

export interface Share {
    post: string;
}