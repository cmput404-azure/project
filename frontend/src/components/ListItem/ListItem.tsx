// @ts-nocheck
import axios from 'axios';
import styles from './ListItem.module.scss';
import { checkAuth } from '../../util/auth/checkauth';
import React, { useEffect, useState } from 'react';

interface ListItemProps {
    isRequest: boolean;
    isPost: boolean;
    isLike: boolean;
    isFollowerList: boolean;
    isUserList:boolean;
    notif_id?:string;
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
    notif_id,
    user
}: ListItemProps) {
    const [userId, setuserId] = useState<string>('');

    useEffect(() => {
        const getUserId = async()=>{
            try {
                let response = await checkAuth();
                if (response) {
                  let userId = response.uuid;
                  console.log(userId);
                  setuserId(userId);
                } else {
                  console.error("checkAuth returned no response.");
                }
              } catch (error) {
                console.error("Error fetching user ID:", error);
              }
        };
        getUserId();

      }, []);
    
    const unFollow = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            const response = await axios.delete(`http://127.0.0.1:8000/api/authors/${userId}/followers/${encodedUrl}/`, {
            });
  
            const data = response.data;
            console.log(data);
 
        } catch (error) {
            console.error('Fetch error:', error);  
        }
    };   

    const sendFollowerRequest = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            // Get the current user info
            const userResponse = await axios.get(`http://127.0.0.1:8000/api/authors/${userId}/`);
            const userInfo = userResponse.data;

            const followRequest = {
                type: "follow",
                summary: `${userInfo.displayName} wants to follow ${user.displayName}`,
                actor: {
                    type: "author",
                    id: `${userInfo.id}`,
                    host: `${userInfo.host}`,
                    displayName: `${userInfo.displayName}`, 
                    github: `${userInfo.github}`,
                    page:`${userInfo.page}`
                },
            }
            await axios.post(`http://127.0.0.1:8000/api/authors/${user.id}/inbox/`, followRequest);
 
        } catch (error) {
            console.error('Fetch error:', error);  
        }
    };   

    const declineFollower = async()=>{
        deleteFollowRequest();

    }

    const addFollower = async()=>{
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;
        // Add actor as follower
        const response = await axios.put(`http://127.0.0.1:8000/api/authors/${userId}/followers/${encodedUrl}/`, {
        });

        const data = response.data;

        // TODO:Delete from inbox after
       await deleteFollowRequest();
       
    }

    const deleteFollowRequest = async()=>{
        const deletefollowRequest = {
            "type": "follow",
            "id": notif_id
        };

        const deleteResponse = await axios.delete(`http://127.0.0.1:8000/api/authors/${userId}/inbox/`,{data: deletefollowRequest})

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