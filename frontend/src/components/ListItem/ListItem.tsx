// @ts-nocheck

import React, { useEffect, useState } from 'react';

import axios from 'axios';
import getCsrfToken from "../../util/auth/getCSRF";
import styles from './ListItem.module.scss';
import { useAuth } from "../../state";

interface ListItemProps {
    isRequest: boolean;
    isPost: boolean;
    isLike: boolean;
    isFollowerList: boolean;
    isUserList: boolean;
    notif_id?: string;
    user: {
        displayName: string;
        github: string;
        host: string;
        id: string; // use the host and id to get the foreign fqid
        page: string;
        type: string;
        profileImage: string | null;
    };
}

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

const csrfToken = getCsrfToken();
const config = {
    headers: {
    "x-csrftoken": csrfToken,
    },
};
export default function ListItem({
    isRequest,
    isPost,
    isLike,
    isFollowerList,
    isUserList,
    notif_id,
    user
}: ListItemProps) {
    const authProvider = useAuth();
    const [isRequested, setIsRequested] = useState(false);

    useEffect(() => {
        // TODO: NEED TO CHECK IF USER HAS REQUESTED ALREADY
    }, [isRequested]);

    const unFollow = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

        try {
            const response = await axios.delete(`http://localhost:8000/api/authors/${authProvider.user.uuid}/followers/${encodedUrl}/`, config);

            const data = response.data;
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
            const userResponse = await axios.get(`http://localhost:8000/api/authors/${authProvider.user.uuid}/`, config);
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
                    page: `${userInfo.page}`
                },
            }
            await axios.post(`http://localhost:8000/api/authors/${user.id}/inbox/`, followRequest, config);
            setIsRequested(true);
        } catch (error) {
            console.error('Fetch error:', error);
        }
    };

    const declineFollower = async () => {
        deleteFollowRequest();

    }

    const addFollower = async () => {
        const encodedHost = encodeURIComponent(user.host);
        const encodedId = encodeURIComponent(user.id);

        const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;
        // Add actor as follower
        const response = await axios.put(`http://localhost:8000/api/authors/${authProvider.user.uuid}/followers/${encodedUrl}/`, config);

        const data = response.data;

        // TODO:Delete from inbox after
        await deleteFollowRequest();

    }

    const deleteFollowRequest = async () => {
        const deletefollowRequest = {
            "type": "follow",
            "id": notif_id
        };

        const deleteResponse = await axios.delete(`http://localhost:8000/api/authors/${authProvider.user.uuid}/inbox/`, { data: deletefollowRequest }, config);

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
                <img className={styles.listImg} src={user.profileImage ?? `https://ui-avatars.com/api/?background=random&name=${user.displayName}`} alt='pfp' />
                <div className={styles.text}>
                    <h1>{user.displayName}
                        <span className={styles.additionalText}>{additionalText}</span>
                    </h1>
                    <p>@{user.displayName}</p>
                </div>

                {isFollowerList ? <button onClick={unFollow}>Unfollow</button> : null}
                {isUserList ? <button onClick={sendFollowerRequest}>{isRequested ? "Requested" : "Follow"}</button> : null}

                {isRequest ? <span><button onClick={addFollower}>Accept</button> <button onClick={declineFollower}>Decline</button></span> : null}
                {isPost ? <img className={styles.listImgPost} src={user.profileImage ?? `https://ui-avatars.com/api/?background=random&name=${user.displayName}`}  alt='pfp' /> : null}
            </div>
        </div>
    )
}