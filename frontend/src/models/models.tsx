import  {ContentType} from "./modelTypes"

export interface Author {
    type: string;
    id: string;
    host: string;
    displayName: string;
    github?: string | null;
    profileImage?: string | null;
    page: string;
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

export interface Post {
    type?: string | "post";
    title: string;
    id: string;
    description: string;
    content: string;
    author: Author;
    contentType: ContentType;
    comments?: Comment[] | null;
    likes?: Like[] | null;
    published: string;
    visibility: number;
}

// This might be one of the four: post, like, comment and request so I simply store all the possible variables
export interface InboxItem {
    type: string;
    title: string;
    id: string;
    description: string;
    author: Author;
    contentType: ContentType;
    comments: Comment[];
    likes: Like[];
    published: string;
    visibility: number;
    comment: string;
    post: string;
    object: string | Author;
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
}

export interface Inbox {
    user: string;
    type: string;
    items: InboxItem[]
}
