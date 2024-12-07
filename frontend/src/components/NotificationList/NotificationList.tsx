// @ts-nocheck

import React, { useCallback, useEffect, useState } from "react";

import { CircularProgress } from "@mui/material";
import ListItem from "../ListItem/ListItem";
import Modal from "react-modal";
import { api } from "../../service/config";
import inbox from "../../service/inbox";
import styles from "./NotificationList.module.scss";
import { useAuth } from "../../state";

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
          if (item === null){
            return null;
          }
          if (item.type === "follow") {
            user = item["actor"]
          } else if (item.type === "like") {
            user = item["author"]
            // Expected format for author's host: http://host/api/
            // Expected format for object: http://host/api/authors/<author_uuid>/posts/<post_uuid>
            try {
              // post should be local 
              let post_resp = await api.get(item.object);
              post_obj = post_resp.data;

              //item.author.id is the author of the like
              if (item.author.id.includes(authProvider.user.uuid) === true) {
                // user liked their own post, don't need to notify
                return null
              }
            } catch {
              // post got deleted
              return null
            }
          } else if (item.type === "comment") {
            user = item["author"]
            try {
              let post_resp = await api.get(item.post);
              post_obj = post_resp.data;

              if (item.author.id.includes(authProvider.user.uuid) === true) {
                // user commented on their own post, don't need to notify
                return null
              }
            } catch {
              // post got deleted
              return null
            }
          }
          else if (item.type === "post") {
            // Someone posted 
            user = item["author"];
            post_obj = item;
          }
          return { ...item, user, post_obj };
        })
      );
      const validNotifications = notificationsWithUsers.filter((notification) => notification !== null);
      console.log("NOTIFICATONS", validNotifications);
      setNotifications(validNotifications);
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

  return (
    <div className={styles.notifications}>
      {loading ? (
        <div className={"loading_component"}><CircularProgress sx={{ color: "#70ffaf" }} /></div>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className={styles.notifications__list}>
          {notifications.length === 0 ? (
            // Display this message when there are no notifications
            <p className={styles.noNotifications}>No notifications to display</p>
          ) :
            (
              notifications.map((item, index) => {
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
                      isLike={true}
                      notif_id={item.id}
                      postObj={item.post_obj}
                      user={item.user}
                      onRefresh={handleRefresh}
                    />
                  );
                } else if (item.type === "comment") {
                  return (
                    <ListItem
                      key={index}
                      isComment={true}
                      notif_id={item.id}
                      postObj={item.post_obj}
                      user={item.user}
                      onRefresh={handleRefresh}
                    />
                  );
                }
                else if (item.type === "post") {
                  return (
                    <ListItem
                      key={index}
                      isPost={true}
                      notif_id={item.id}
                      postObj={item.post_obj}
                      user={item.user}
                      onRefresh={handleRefresh}
                    />
                  );
                }
                return null;
              })
            )
          }
        </div>
      )}
    </div>
  );
}  
