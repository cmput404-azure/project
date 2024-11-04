// @ts-nocheck

import { Link, useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";

import { Avatar } from "@mui/material";
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import styles from "./ListItem.module.scss";
import { useAuth } from "../../state";
import FollowService from "../../service/follow";
import InboxService from "../../service/inbox";
interface ListItemProps {
  isRequest: boolean;
  isPost: boolean;
  postTitle?: string;
  isLike: boolean;
  isComment?:boolean;
  isShare?:boolean;
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
    has_requested?: boolean;
  };
  closeModal?: () => void;
  onRefresh: () => void;
}

export default function ListItem({
  isRequest,
  isPost,
  postTitle,
  isLike,
  isShare,
  isComment,
  isFollowerList,
  isUserList,
  notif_id,
  user,
  closeModal,
  onRefresh,
}: ListItemProps) {
  const authProvider = useAuth();
  const [isRequested, setIsRequested] = useState(false);
  const navigate = useNavigate();
  const [userId, setUserId] = useState("");
  useEffect(()=>{
    const fetchData = async () => {
      // Format the user ID
      let formatted_userId = user.id.replace(/\/+$/, '').split('/').pop();
      setUserId(formatted_userId);
  
      // Check inbox of the user ID
      const userInbox = await InboxService.getInbox(formatted_userId);
      await Promise.all(
        userInbox.map(async (item: any) => {
          if (item && item.type === "follow") {
            let actorId = item.actor.id.replace(/\/+$/, '').split('/').pop();
            if (actorId===authProvider.user.uuid){
              setIsRequested(true);
            }
          }
        })
      );

    };
  
    fetchData(); // Call the async function
  }, []);

  const unFollow = async () => {
    await FollowService.unfollow(user.id, authProvider.user);
    onRefresh();
  };

  const sendFollowerRequest = async () => {

    try {
      const userResponse = await api.get(`/api/authors/${authProvider.user.uuid}/`);
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
          page: `${userInfo.page}`,
        },
      };

      await InboxService.sendPostToInbox(user.id, followRequest);
      setIsRequested(true);
    } catch (error) {
      console.error("Fetch error:", error);
    }
  };

  const addFollower = async () => {
    const encodedId = encodeURIComponent(user.id);
    await FollowService.addFollower(authProvider.user.uuid, encodedId)
    await deleteFollowRequest();
    onRefresh();
  };

  const deleteFollowRequest = async () => {
    try {
      await InboxService.deleteInboxFollowRequest(authProvider.user.uuid,notif_id);
      onRefresh();
    } catch (error) {
      console.error("Delete follow request error:", error);
    }
  };

  const navigateToProfile = () => {
    closeModal?.();
    navigate(`/authors/${extractUUID(user.id)}`);
  };

  let additionalText = "";
  if (isRequest) additionalText = "wants to follow you";
  else if (isLike) additionalText = `liked your post titled: ${postTitle}`;
  else if (isShare) additionalText = `shared a post with you titled: ${postTitle}`;
  else if (isPost) additionalText = `posted a post titled: ${postTitle}`;
  else if (isComment) additionalText = `commented on your post titled: ${postTitle}`;

  return (
    <div className={styles.ListItemContainer}>
      <div className={styles.container}>
        <div className={styles.profileLink} onClick={navigateToProfile}>
          <Avatar
            className={styles.listImg}
            alt={user.displayName}
            src={user.profileImage}
            sx={{ width: 48, height: 48 }}
          />
          <div className={styles.text}>
            <h1>
              {user.displayName}
              <span className={styles.additionalText}>{additionalText}</span>
            </h1>
            <p>@{user.displayName}</p>
          </div>
        </div>

        {isFollowerList && <button onClick={unFollow}>Unfollow</button>}

        {isUserList && (
          <button
            onClick={sendFollowerRequest}
            disabled={isRequested || user.has_requested}
          >
            {isRequested || user.has_requested ? "Requested" : "Follow"}
          </button>
        )}

        {isRequest && (
          <div className={styles.buttonGroup}>
            <button onClick={addFollower}>Accept</button>{" "}
            <button onClick={deleteFollowRequest}>Decline</button>
          </div>
        )}
      </div>
    </div>
  );
}
