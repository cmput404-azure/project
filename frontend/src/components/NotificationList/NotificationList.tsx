// @ts-nocheck
import { CircularProgress } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";

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
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true); // Track if more pages are available
  const notificationsPerPage = 5;

  const authProvider = useAuth();

  const fetchNotifications = useCallback(
    async (page: number = 1) => {
      try {
        setLoading(true);

        // Fetch paginated data
        const response = await inbox.getInboxPaginated(
          authProvider.user.uuid,
          page,
          notificationsPerPage
        );
        const { items } = response; // Adjust based on your API response format

        // Fetch additional user/post details for each item
        const notificationsWithUsers = await Promise.all(
          response.map(async (item: any) => {
            let user = null;
            let post_obj = null;

            if (item.type === "follow") {
              user = await fetchUser(item.actor.id);
            } else if (item.type === "like" || item.type === "comment") {
              user = await fetchUser(item.author.id);
              try {
                const postResp = await api.get(item.object || item.post);
                post_obj = postResp.data;
              } catch {
                return null; // Skip deleted posts
              }
            } else if (item.type === "post") {
              const userResp = await api.get(item.author.id);
              user = userResp.data;
              post_obj = item;
            }
            return { ...item, user, post_obj };
          })
        );

        const validNotifications = notificationsWithUsers.filter(
          (notification) => notification !== null
        );

        // Deduplicate notifications based on their `id`
        setNotifications((prev) => {
          const notificationMap = new Map(
            [...prev, ...validNotifications].map((n) => [n.id, n])
          );
          return Array.from(notificationMap.values());
        });

        setHasMore(validNotifications.length === notificationsPerPage); // Check if we received a full page
      } catch (err) {
        console.error("Error fetching notifications:", err);
        setError("Failed to fetch notifications");
      } finally {
        setLoading(false);
      }
    },
    [authProvider.user.uuid]
  );

  useEffect(() => {
    fetchNotifications(currentPage);
  }, [fetchNotifications, currentPage]);

  const fetchUser = async (id: string) => {
    try {
      const response = await api.get(`/api/authors/${id}/`);
      return response.data;
    } catch (err) {
      console.error(`Error fetching user with id: ${id}:`, err);
      return null;
    }
  };

  const loadMoreNotifications = () => {
    if (hasMore) {
      setCurrentPage((prevPage) => prevPage + 1);
    }
  };

  return (
    <div className={styles.notifications}>
      {loading && currentPage === 1 ? (
        <div className={"loading_component"}>
          <CircularProgress sx={{ color: "#70ffaf" }} />
        </div>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className={styles.notifications__list}>
          {notifications.length === 0 ? (
            <p className={styles.noNotifications}>
              No notifications to display
            </p>
          ) : (
            notifications.map((item, index) => (
              <ListItem
                key={item.id} // Ensure key is unique
                isRequest={item.type === "follow"}
                isPost={item.type === "post"}
                isLike={item.type === "like"}
                isComment={item.type === "comment"}
                notif_id={item.id}
                user={item.user}
                postObj={item.post_obj}
                onRefresh={() => fetchNotifications(1)} // Refresh all data
              />
            ))
          )}
          {hasMore ? (
            <button
              className={styles.loadMoreButton}
              onClick={loadMoreNotifications}
            >
              Load More
            </button>
          ) : (
            <div className={styles.noNotifications}>No more notifications</div>
          )}
        </div>
      )}
    </div>
  );
}
