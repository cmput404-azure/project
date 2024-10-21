// @ts-nocheck
import React, { useEffect, useState } from 'react';

import ListItem from '../ListItem/ListItem';
import Modal from 'react-modal';
import axios from 'axios';
import styles from './NotificationList.module.scss';
import { checkAuth } from '../../util/auth/checkauth';


interface FollowerResponse {
    followers: Follower[];
}

Modal.setAppElement('#root');

export default function NotificationList() {
    const [notifications, setNotifications] = useState<Follower[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [userId, setuserId] = useState<string>('');

    useEffect(() => {
        const getUserId = async () => {
            try {
                const response = await checkAuth();
                if (response) {
                    const userId = response.uuid;
                    console.log(userId);
                    setuserId(userId); // Update userId state
                    fetchNotifications(userId); // Fetch notifications after setting userId
                } else {
                    console.error("checkAuth returned no response.");
                }
            } catch (error) {
                console.error("Error fetching user ID:", error);
            }
        };
    
        const fetchNotifications = async (id: string) => {
            try {
                const userResponse = await axios.get(
                    `http://127.0.0.1:8000/api/authors/${id}/inbox/`
                );
                const notificationsWithUsers = await Promise.all(
                    userResponse.data.items.map(async (item: any) => {
                        if (item.type === "follow") {
                            const user = await fetchUser(item.actor.id); // Fetch user object
                            return { ...item, user }; // Include user info in the item
                        }
                        return item;
                    })
                );
                setNotifications(notificationsWithUsers);
                console.log(notificationsWithUsers);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching notifications:", err);
                setError("Failed to fetch notifications");
                setLoading(false);
            }
        };
    
        getUserId(); // Call getUserId when the component mounts
    }, []);

    
    const fetchUser = async (userId: string) => {
        try {
            const response = await axios.get(
                `http://127.0.0.1:8000/api/authors/${userId}/`
            );
            return response.data;
        } catch (err) {
            console.error(`Error fetching user ${userId}:`, err);
            return null; // Handle failure gracefully
        }
    };


    return (
        <div>
            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <ul className={styles.ul}>
                    {notifications.map((item, index) =>
                        item.type === "follow" ? (
                            <ListItem
                                key={index}
                                isRequest={true}
                                isPost={false}
                                isLike={false}
                                isFollowerList={false}
                                isUserList={false}
                                notif_id = {item.id}
                                user={item.user}
                            />
                        ) : (
                            <ListItem
                                key={index}
                                isRequest={false}
                                isPost={true} // Example: Different logic for posts
                                isLike={false}
                                isFollowerList={false}
                                isUserList={false}
                                notif_id = {item.id}
                                user={item.user} // Adjust logic based on type
                            />
                        )
                    )}
                </ul>
            )}
        </div>
    );
}