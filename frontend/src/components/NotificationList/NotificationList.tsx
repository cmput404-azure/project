// @ts-nocheck
import React, { useCallback, useEffect, useState } from "react";

import { CircularProgress } from "@mui/material";
import ListItem from "../ListItem/ListItem";
import Modal from "react-modal";
import { api } from "../../service/config";
import inbox from "../../service/inbox";
import PostService from "../../service/post"
import styles from "./NotificationList.module.scss";
import { useAuth } from "../../state";

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
          let post_obj = null;
          if (item.type === "follow") {
            user = await fetchUser(item.actor.id);
          } else if (item.type === "like") {
            user = await fetchUser(item.author.id);
            // Expected format for host: http://host/api/
            // Expected format for object: api/authors/author_id/posts/post_id
            const objectPath = item.object.startsWith("api/") ? item.object.slice(4) : item.object;
            let post_resp = await api.get(`${item.author.host}${objectPath}`);
            post_obj = post_resp.data;
          }else if (item.type === "comment"){
            user = await fetchUser(item.author.id);
            let post_resp = await api.get(item.post);
            post_obj = post_resp.data;
          }
          return { ...item, user, post_obj };
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
        <div className={"loading_component"}><CircularProgress/></div>
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
                    postTitle = {item.post_obj.title}
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
                    postTitle = {item.post_obj.title}
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
