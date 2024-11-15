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
import ProfileService from "../../service/profile";
import { PostData, Author } from "../../models/models"
import { normalizeURL } from "../../util/formatting/normalizeURL";

interface ListItemProps {
  isRequest?: boolean;
  isPost?: boolean;
  postObj?: PostData;
  isLike?: boolean;
  isComment?: boolean;
  isFollowerList?: boolean;
  isUserList?: boolean;
  notif_id?: string;
  user: Author;
  closeModal?: () => void;
  onRefresh: () => void;
}

export default function ListItem({
  isRequest,
  isPost,
  postObj,
  isLike,
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
  const [isFollowing, setIsFollowing] = useState(false);
  const [isUpdatedPost, setIsUpdatedPost] = useState(false);
  const [isDeletedPost, setIsDeletedPost] = useState(false);
  const navigate = useNavigate();
  const [userId, setUserId] = useState("");
  const [isRemote, setIsRemote] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      // Format the user ID
      let formatted_userId = user.id.replace(/\/+$/, '').split('/').pop();
      setUserId(formatted_userId);

      let test_host = user.host.replace("api/", "");
      if (test_host != process.env.REACT_APP_API_BASE_URL) {
        setIsRemote(true);
      }
      // Check inbox of the user ID
      let userInbox = null;
      if (isRemote === true){
        userInbox = await InboxService.getRemoteInbox(user.host, formatted_userId)
      }else{
        userInbox = await InboxService.getInbox(formatted_userId);
      }
      await Promise.all(
        userInbox.map(async (item: any) => {
          if (item && item.type === "follow") {
            let actorId = item.actor.id.replace(/\/+$/, '').split('/').pop();
            if (actorId === authProvider.user.uuid) {
              setIsRequested(true);
            }
          }
        })
      );

      // check if current user is already following the user
      const currentUser = await ProfileService.fetchAuthorData(authProvider.user.uuid);
      const encoded_url = encodeURIComponent(currentUser.id);
      const following = await FollowService.checkFollowing(formatted_userId, encoded_url);

      if (following === true) {
        setIsFollowing(true);
      }

    };

    if (authProvider.isAuthenticated === true) {
      if (isUserList) {
        fetchData(); // Call the async function
      }
      if (postObj != null) {
        if (postObj.post_status === "update") {
          setIsUpdatedPost(true);
        } else if (postObj.post_status === "delete") {
          setIsDeletedPost(true);
        }
      }
    }
  }, []);

  const unFollow = async () => {
    await FollowService.unfollow(user.id, authProvider.user);
    onRefresh();
  };

  const sendFollowerRequest = async () => {
    if (authProvider.isAuthenticated === true) {
      try {
        const userResponse = await api.get(`/api/authors/${authProvider.user.uuid}/`);
        const userInfo = userResponse.data;

        const followRequest = {
          type: "follow",
          summary: `${userInfo.username} wants to follow ${user.username}`,
          actor: {
            type: "author",
            id: `${userInfo.id}`,
            host: `${userInfo.host}`,
            displayName: `${userInfo.displayName}`,
            username: `${userInfo.username}`,
            bio: `${userInfo.bio}`,
            profileImage: `${userInfo.profileImage}`,
            github: `${userInfo.github}`,
            page: `${userInfo.page}`,
          },
          object: {
            type:"author",
            id: `${user.id}`,
            host: `${user.host}`,
            displayName: `${user.displayName}`,
            username: `${user.username}`,
            bio: `${user.bio}`,
            profileImage: `${user.profileImage}`,
            github: `${user.github}`,
            page: `${user.page}`,
          }
        };

          await InboxService.sendPostToInbox(user.id, followRequest);
      } catch (error) {
        console.error("Fetch error:", error);
      }

      setIsRequested(true);

    } else {
      closeModal?.();
      navigate("/login");
    }
  }

  const addFollower = async () => {
    const encodedId = encodeURIComponent(user.id);
    await FollowService.addFollower(authProvider.user.uuid, encodedId)
    await deleteFollowRequest();
    onRefresh();
  };

  const deleteFollowRequest = async () => {
    try {
      await InboxService.deleteInboxFollowRequest(authProvider.user.uuid, notif_id);
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
  else if (isLike) additionalText = `liked your post titled: ${postObj.title}`;
  else if (isComment) additionalText = `commented on your post titled: ${postObj.title}`;
  else if (isUpdatedPost) additionalText = `updated their post titled: ${postObj.title}`;
  else if (isDeletedPost) additionalText = `deleted their post titled: ${postObj.title}`;
  else if (isPost) additionalText = `posted a post titled: ${postObj.title}`;

  return (
    <div className={styles.ListItemContainer}>
      <div className={styles.container}>
        <div className={styles.profileLink} onClick={navigateToProfile}>
          <Avatar
            className={styles.listImg}
            alt={user.username}
            src={user.profileImage}
            sx={{ width: 48, height: 48 }}
          />
          <div className={styles.text}>
            <h1>
              {user.username}
              <span className={styles.additionalText}>{additionalText}</span>
            </h1>
            <p>@{user.username}</p>
          </div>
        </div>

        {isFollowerList && <button onClick={unFollow}>Unfollow</button>}

        {isUserList && (
          <button
            onClick={sendFollowerRequest}
            disabled={isRequested || isFollowing}
          >
            {isFollowing
              ? "Following"
              : isRequested
                ? "Requested"
                : "Follow"}
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
