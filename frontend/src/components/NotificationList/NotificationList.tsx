// @ts-nocheck
import React, { useEffect, useState } from "react";

import ListItem from "../ListItem/ListItem";
import Modal from "react-modal";
import axios from "axios";
import styles from "./NotificationList.module.scss";
import { useAuth } from "../../state";
import { api } from "../../service/config";

interface FollowerResponse {
  followers: Follower[];
}

Modal.setAppElement("#root");

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
        const userResponse = await api.get(
          `/api/authors/${authProvider.user.uuid}/inbox/`
        );
        const notificationsWithUsers = await Promise.all(
          userResponse.data.items
            .filter((item: any) => item.type === "follow")
            .map(async (item: any) => {
              const user = await fetchUser(item.actor.id);
              return { ...item, user };
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

    fetchNotifications();
  }, []);

  const fetchUser = async (id: string) => {
    try {
      const response = await api.get(`/api/authors/${id}/`);
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
        <div>
        <h2 className = {styles.h2}>Notifications</h2>
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
                notif_id={item.id}
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
                notif_id={item.id}
                user={item.user} // Adjust logic based on type
              />
            )
          )}
        </ul>
      </div>
      )
      
      }
    </div>
  );
}
