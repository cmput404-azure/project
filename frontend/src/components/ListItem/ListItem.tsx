import axios from 'axios';
import styles from './ListItem.module.scss';

interface ListItemProps {
    isRequest: boolean;
    isPost: boolean;
    isLike: boolean;
    isFollowerList: boolean;
    isUserList:boolean;
    user: {
        displayName: string;          // Make sure this matches your follower object structure
        github: string;
        host: string;
        id: string; // use the host and id to get the foreign fqid
        page: string;
        type:string;
    };}

export default function ListItem({
    isRequest,
    isPost,
    isLike,
    isFollowerList,
    isUserList,
    user
}: ListItemProps) {
    const unFollow = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            const response = await axios.delete(`http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/followers/${encodedUrl}/`, {
            });
  
            const data = response.data;
            console.log(data);
 
        } catch (error) {
            console.error('Fetch error:', error);  
        }
    };   

    const follow = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            const response = await axios.put(`http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/followers/${encodedUrl}/`, {
            });
  
            const data = response.data;
            console.log(data);
 
        } catch (error) {
            console.error('Fetch error:', error);  
        }
    };   

    
    let additionalText = "";

    if (isFollowerList) {
        additionalText = "accepted your follow request";
    } else if (isRequest) {
        additionalText = "wants to follow you";
    }
    else if (isLike) {
        additionalText = "liked your post";
    } else if (isPost) {
        additionalText = "shared a post with you";
    }
    return (
        <div className={styles.ListItemContainer}>
            <div className={styles.container}>
                <img className={styles.listImg} src='../images/Shiba-pfp.jpg' alt='pfp' />
                <div className={styles.text}>
                    <h1>{user.displayName}
                    <span className={styles.additionalText}>{additionalText}</span>
                    </h1>
                    <p>@{user.displayName}</p>
                </div>

                {isFollowerList ? <button onClick={unFollow}>Unfollow</button> : null}
                {isUserList ? <button onClick={follow}>Follow</button> : null}

                {isRequest ? <span><button>Accept</button> <button>Decline</button></span> : null}
                {isPost ? <img className={styles.listImgPost} src='../images/Shiba-pfp.jpg' alt='pfp' /> : null}
            </div>
        </div>
    )
}