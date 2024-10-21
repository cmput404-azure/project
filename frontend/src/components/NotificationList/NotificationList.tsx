// @ts-nocheck
import React, { useEffect, useState } from 'react';

import ListItem from '../ListItem/ListItem';
import Modal from 'react-modal';
import axios from 'axios';
import styles from './NotificationList.module.scss';
import { useAuth } from "../../state";


interface FollowerResponse {
    followers: Follower[];
}

Modal.setAppElement('#root');

export default function NotificationList() {
    const [notifications, setNotifications] = useState<Follower[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const authProvider = useAuth();

    axios.defaults.withCredentials = true;
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "x-csrftoken";
    useEffect(() => {
    
        const fetchNotifications = async (id: string) => {
            try {
                const userResponse = await axios.get(
                    `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/inbox/`
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
    
        fetchNotifications()
    }, []);

    
    const fetchUser = async () => {
        try {
            const response = await axios.get(
                `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/`
            );
            return response.data;
        } catch (err) {
            console.error(`Error fetching user ${authProvider.user.uuid}:`, err);
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