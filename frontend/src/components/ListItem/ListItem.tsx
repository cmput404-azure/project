// @ts-nocheck

import { Author, PostData } from "../../models/models"
import React, { useEffect, useState } from "react";

import { Avatar } from "@mui/material";
import FollowService from "../../service/follow";
import InboxService from "../../service/inbox";
import { api } from "../../service/config";
import { extractHost } from "../../util/formatting/extractHost";
import { extractUUID } from "../../util/formatting/extractUUID";
import { normalizeURL } from "../../util/formatting/normalizeURL";
import profileService from "../../service/profile";
import styles from "./ListItem.module.scss";
import { useAuth } from "../../state";
import { useNavigate } from "react-router-dom";

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

  useEffect(() => {
    const fetchData = async () => {
      const userListId = extractUUID(user.id);
      setUserId(userListId);
      
      let following = false;

      if (normalizeURL(user.host) === normalizeURL(process.env.REACT_APP_API_BASE_URL)) {
        // check if current user is already following the (local) user
        const loggedInFQID = `${authProvider.user.host}/api/authors/${authProvider.user.uuid}`
        const encodedURL = encodeURIComponent(loggedInFQID);
        following = await FollowService.checkFollowing(extractUUID(user.id), encodedURL);
      } else {
        try {
          following = await api.get(`/api/check/${authProvider.user.uuid}/follows/${user.id}`);
        } catch (err) {
          if (err.response.status !== 404) {
            console.error('Fetch following error:', error);
          }
        }
      }

      if (following) {
        setIsFollowing(true);
      }
    };

    async function checkRequested() {
      // Check inbox of the user ID
      if (normalizeURL(user.host) === normalizeURL(process.env.REACT_APP_API_BASE_URL)) {
        const userInbox = await InboxService.getInbox(extractUUID(user.id));
        await Promise.all(
          userInbox.map(async (item: any) => {
            if (item && item.type === "follow") {
              let actorId = item.actor.id.replace(/\/+$/, "").split("/").pop();
              if (actorId === authProvider.user.uuid) {
                setIsRequested(true);
              }
            }
          })
        );
      }
    }

    if (authProvider.isAuthenticated) {
      if (isUserList) {
        fetchData(); // Call the async function
        checkRequested();
      }
      if (postObj != null) {
        if (postObj.post_status && postObj.post_status.includes("update")) {
          setIsUpdatedPost(true);
        } else if (postObj.post_status === "delete") {
          setIsDeletedPost(true);
        }
      }
    }
  }, []);

  const unfollow = async () => {
    await FollowService.unfollow(user.id, authProvider.user);
    onRefresh();
  };

  const sendFollowerRequest = async () => {
    if (!authProvider.isAuthenticated) {
      closeModal?.();
      navigate("/login");
    }
    
    const userResponse = await profileService.fetchAuthorData(authProvider.user.uuid);

    const followRequest = {
      type: "follow",
      summary: `${userResponse.username} wants to follow ${user.displayName}`,
      actor: { // person who sends the request
        type: "author",
        id: `${userResponse.id}`,
        host: `${userResponse.host}`,
        displayName: `${userResponse.displayName}`,
        username: userResponse.username || "",
        bio: userResponse.bio || "",
        profileImage: `${userResponse.profileImage}`,
        github: `${userResponse.github}`,
        page: `${userResponse.page}`,
      },
      object: { // person who the request is being sent to
        type: "author",
        id: `${user.id}`,
        host: `${user.host}`,
        displayName: `${user.displayName}`,
        username: user.username || "",
        bio: user.bio || "",
        profileImage: `${user.profileImage}`,
        github: `${user.github}`,
        page: `${user.page}`,
      }
    };

    await InboxService.sendPostToInbox(user.id, followRequest);

    setIsRequested(true);
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
    let user_url = user["id"]
    if (normalizeURL(user_url) === normalizeURL(process.env.REACT_APP_API_BASE_URL)) {
      navigate(`/authors/${extractUUID(user.id)}`);
    } else {
      // To-do: Fetch correct information (posts, followers, followings, friends)
      const encodedUserId = encodeURIComponent(user_url);
      navigate(`/authors/${encodedUserId}`);
    }
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
          <div className="avatar">
            <Avatar
              className={styles.listImg}
              alt="User icon"
              src={profileService.getProfilePicture(user)}
              sx={{ width: 48, height: 48 }}
            />
          </div>
          <div className={styles.text}>
            <h1>
              {user.displayName ?? extractHost(user.host)}
              <span className={styles.additionalText}>{additionalText}</span>
            </h1>
            <p>@{user.username ?? extractHost(user.host)}</p>
          </div>
        </div>

        {isFollowerList && <button onClick={unfollow}>Unfollow</button>}

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
