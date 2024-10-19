import axios from 'axios';
import styles from './ListItem.module.scss';

interface ListItemProps {
    isRequest: boolean;
    isPost: boolean;
    isLike: boolean;
    isFollowerList: boolean;
    isUserList:boolean;
    user: {
        displayName: string;          
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

    const sendFollowerRequest = async () => {
        const tmpUserId="b2ec57e0-fce1-4fd0-8cff-e347efe528aa";
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            // Get the current user info
            const userResponse = await axios.get(`http://127.0.0.1:8000/api/authors/${tmpUserId}/`);
            const userInfo = userResponse.data;

            const followRequest = {
                type: "follow",
                summary: `${user.displayName} wants to follow ${userInfo.displayName}`,
                actor: {
                    type: "author",
                    id: `${user.id}`,
                    host: `${user.host}`,
                    displayName: `${user.displayName}`, 
                    github: `${user.github}`,
                    page:`${user.page}`
                },
            }
            await axios.post(`http://127.0.0.1:8000/api/authors/${tmpUserId}/inbox/`, followRequest);

           
 
        } catch (error) {
            console.error('Fetch error:', error);  
        }
    };   

    const declineFollower = async()=>{
       
        // TODO:Delete from inbox after

    }

    const addFollower = async()=>{
        const tmpUserId="b2ec57e0-fce1-4fd0-8cff-e347efe528aa";
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;
        // Add actor as follower
         const response = await axios.put(`http://127.0.0.1:8000/api/authors/${tmpUserId}/followers/${encodedUrl}/`, {
        });

        const data = response.data;

        // TODO:Delete from inbox after

    }

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
                {isUserList ? <button onClick={sendFollowerRequest}>Follow</button> : null}

                {isRequest ? <span><button onClick={addFollower}>Accept</button> <button onClick = {declineFollower}>Decline</button></span> : null}
                {isPost ? <img className={styles.listImgPost} src='../images/Shiba-pfp.jpg' alt='pfp' /> : null}
            </div>
        </div>
    )
}