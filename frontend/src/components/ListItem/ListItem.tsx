// @ts-nocheck

import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../service/config";
import styles from "./ListItem.module.scss";
import { useAuth } from "../../state";

interface ListItemProps {
  isRequest: boolean;
  isPost: boolean;
  isLike: boolean;
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
  isLike,
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

  const unFollow = async () => {
    const encodedHost = encodeURIComponent(user.host);
    const encodedId = encodeURIComponent(authProvider.user.uuid);
    const url = `${encodedHost}/api/authors/${encodedId}`;
    const encodedUrl = encodeURIComponent(url);

    try {
      const response = await api.delete(`/api/authors/${user.id}/followers/${encodedUrl}/`);
      const data = response.data;
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const sendFollowerRequest = async () => {
    const encodedHost = encodeURIComponent(user.host);
    const encodedId = encodeURIComponent(user.id);
    const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

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

      await api.post(`/api/authors/${user.id}/inbox/`, followRequest);
      setIsRequested(true);
    } catch (error) {
      console.error("Fetch error:", error);
    }
  };

  const addFollower = async () => {
    const encodedHost = encodeURIComponent(user.host);
    const encodedId = encodeURIComponent(user.id);
    const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;

    try {
      await api.put(`/api/authors/${authProvider.user.uuid}/followers/${encodedUrl}/`);
      await deleteFollowRequest();
    } catch (error) {
      console.error("Add follower error:", error);
    }
  };

  const deleteFollowRequest = async () => {
    try {
      const deleteRequest = { type: "follow", id: notif_id };
      console.log(deleteRequest);
      await api.delete(`/api/authors/${authProvider.user.uuid}/inbox/`, { data: deleteRequest });
      onRefresh();
    } catch (error) {
      console.error("Delete follow request error:", error);
    }
  };

  const navigateToProfile = () => {
    closeModal?.();
  };

  let additionalText = "";
  if (isRequest) additionalText = "wants to follow you";
  else if (isLike) additionalText = "liked your post";
  else if (isPost) additionalText = "shared a post with you";

  return (
    <div className={styles.ListItemContainer}>
      <div className={styles.container}>
        <Link to={`/authors/${user.id}`} className={styles.profileLink} onClick={navigateToProfile}>
          <img
            className={styles.listImg}
            src={
              user.profileImage ? user.profileImage.trim() :
              `https://ui-avatars.com/api/?background=random&name=${user.displayName}`
            }
            alt="pfp"
          />
          <div className={styles.text}>
            <h1>
              {user.displayName}
              <span className={styles.additionalText}>{additionalText}</span>
            </h1>
            <p>@{user.displayName}</p>
          </div>
        </Link>

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

        {isPost && (
          <img
            className={styles.listImgPost}
            src={
              user.profileImage ??
              `https://ui-avatars.com/api/?background=random&name=${user.displayName}`
            }
            alt="pfp"
          />
        )}
      </div>
    </div>
  );
}
