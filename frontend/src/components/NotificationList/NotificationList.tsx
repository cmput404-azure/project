// @ts-nocheck
import React, { useCallback, useEffect, useState } from "react";

import { CircularProgress, responsiveFontSizes } from "@mui/material";
import ListItem from "../ListItem/ListItem";
import Modal from "react-modal";
import PostService from "../../service/post"
import { api } from "../../service/config";
import inbox from "../../service/inbox";
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
      console.log("USER RESPONSE", userResponse);

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
          } else if (item.type === "comment") {
            let encodedId = encodeURIComponent(item.author.id);
            user = await fetchUser(encodedId);
            let post_resp = await api.get(item.post);
            post_obj = post_resp.data;
          } 
          // else if (item.type === "share") {
          //   let user_resp = await api.get(item.user);
          //   user = user_resp.data;
          //   let post_resp = await PostService.getPost(item.post);
          //   post_obj = post_resp;
          // } 
          else if (item.type === "post") {
            // Someone shared a friends only post
            let user_resp = await api.get(item.author.id);
            user = user_resp.data;
            post_obj = item;
          }
          return { ...item, user, post_obj };
        })
      );
      console.log("NOTIFICATONS", notificationsWithUsers);
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
      {loading ? (
        <div className={"loading_component"}><CircularProgress sx={{ color: "#70ffaf" }} /></div>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div>
          <ul className={styles.customList}>
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
                    postTitle={item.post_obj.title}
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
                    postTitle={item.post_obj.title}
                    user={item.user}
                    onRefresh={handleRefresh}
                  />
                );
              } 
              // else if (item.type === "share") {
              //   return (
              //     <ListItem
              //       key={index}
              //       isRequest={false}
              //       isPost={true}
              //       isLike={false}
              //       isComment={false}
              //       isShare={true}
              //       isFollowerList={false}
              //       isUserList={false}
              //       notif_id={item.id}
              //       postTitle={item.post_obj.title}
              //       user={item.user}
              //       onRefresh={handleRefresh}
              //     />
              //   );
              // }
              else if (item.type === "post") {
                return (
                  <ListItem
                    key={index}
                    isRequest={false}
                    isPost={true} 
                    isLike={false}
                    isComment={false}
                    isShare = {false}
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
