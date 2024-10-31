// @ts-nocheck
import React, { useEffect, useState, useCallback } from "react";

import ListItem from "../ListItem/ListItem";
import Modal from "react-modal";
import styles from "./NotificationList.module.scss";
import { useAuth } from "../../state";
import { api } from "../../service/config";
import inbox from "../../service/inbox";

interface FollowerResponse {
  followers: Follower[];
}

Modal.setAppElement("#root");

export default function NotificationList() {
  const [notifications, setNotifications] = useState<Follower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const authProvider = useAuth();

  const fetchNotifications = useCallback(async () => {
    try {
      const userResponse = await inbox.getInbox(authProvider.user.uuid);

      const notificationsWithUsers = await Promise.all(
        userResponse.map(async (item: any) => {
          let user = null;
          if (item.type === "follow") {
            user = await fetchUser(item.actor.id);
          } else if (item.type === "like" || item.type==="comment") {
            user = await fetchUser(item.author.id);
          }
          return { ...item, user };
        })
      );
      setNotifications(notificationsWithUsers);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching notifications:", err);
      setError("Failed to fetch notifications");
      setLoading(false);
    }
  }, [authProvider.user.uuid]);


  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications, refreshTrigger]);

  const handleRefresh = () => setRefreshTrigger(prev => prev + 1);

  const fetchUser = async (id: string) => {
    try {
      const response = await api.get(`/api/authors/${id}/`);
      return response.data;
    } catch (err) {
      console.error(`Error fetching user ${authProvider.user.uuid}:`, err);
      return null;
    }
  };

  return (
    <div>
      <h2 className={styles.h2}>Notifications</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div>
          <ul className={styles.ul}>
            {notifications.map((item, index) => {
              if (item.type === "follow") {
                return (
                  <ListItem
                    key={index}
                    isRequest={true}
                    isPost={false}
                    isLike={false}
                    isFollowerList={false}
                    isUserList={false}
                    notif_id={item.id}
                    user={item.user}
                    onRefresh={handleRefresh}
                  />
                );
              } else if (item.type === "like") {
                return (
                  <ListItem
                    key={index}
                    isRequest={false}
                    isPost={false}
                    isLike={true}
                    isFollowerList={false}
                    isUserList={false}
                    notif_id={item.id}
                    user={item.user}
                    onRefresh={handleRefresh}
                  />
                );
              } else if (item.type === "comment") {
                return (
                  <ListItem
                    key={index}
                    isRequest={false}
                    isPost={false} 
                    isLike={false}
                    isComment={true}
                    isFollowerList={false}
                    isUserList={false}
                    notif_id={item.id}
                    user={item.user}
                    onRefresh={handleRefresh}
                  />
                );
              }
              return null; 
            })}
          </ul>
        </div>
      )}
    </div>
  );
}  
