// @ts-nocheck
import React, { useEffect, useState } from 'react';
import follow, { getFollowers, getFollowing, getFriends } from "../../service/follow";

import Author from "../../models/models"
import { CircularProgress } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import ListItem from '../ListItem/ListItem';
import Modal from 'react-modal';
import { api } from "../../service/config";
import styles from './FollowList.module.scss';
import { useAuth } from "../../state";

interface Follower {
  displayName: string;
  github: string;
  host: string;
  id: string; // use the host and id to get the foreign fqid
  page: string;
  type: string;
}

// Define the props for the FollowerList component
interface FollowerListProps {
  isOpen: boolean;
  onClose: () => void;
  isFollowerList: string;
  profileId?: string;
  followersProp?: Follower[];
}

Modal.setAppElement('#root');

export default function FollowList({ isOpen, onClose, isFollowerList, profileId, followersProp, }: FollowerListProps) {
  const [followers, setFollowers] = useState<Follower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const authProvider = useAuth();

  useEffect(() => {
    if (isOpen) {
      if (isFollowerList === 'Follower') {
        fetchFollowers(); // Fetch followers only when the modal is open
        return;
      } else if (isFollowerList === 'Following') {
        fetchFollowing();
      } else {
        fetchFriends();
      }
    }
  }, [isOpen, refreshTrigger]);

  const handleRefresh = () => setRefreshTrigger(prev => prev + 1);

  const fetchFriends = async () => {
    try {
      let data = null;
      if (profileId) {
        data = await follow.getFriends(profileId);
      } else {
        data = await follow.getFriends(authProvider.user.uuid);
      }
      setFollowers(data);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);

    }
  };

  const fetchFollowers = async () => {
    if (followersProp) {
      setFollowers(followersProp)
      setLoading(false)
    } else {
      try {
        let data = null;
        if (profileId) {
          data = await follow.getFollowers(profileId);
        } else {
          data = await follow.getFollowers(authProvider.user.uuid);
        }
        setFollowers(data);
        setLoading(false);
      } catch (error) {
        console.error('Fetch error:', error);
        setLoading(false);
      }
    }
  };

  const fetchFollowing = async () => {
    try {
      let data = null;
      if (profileId) {
        data = await follow.getFollowing(profileId);
      } else {
        data = await follow.getFollowing(authProvider.user.uuid);
      }
      setFollowers(data);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onClose}
      contentLabel="Follower List"
      className={styles.modalContent}
      overlayClassName={styles.modalOverlay}
    >
      <div className={styles.modalHeader}>
        <h2 className={styles.modalTitle}>{isFollowerList}</h2>
        <button onClick={onClose} className={styles.closeModalButton}>
          <CloseIcon style={{ fontSize: "14px" }} />
        </button>
      </div>
      {loading ? (
        <div className={"loading_component"}><CircularProgress /></div>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <ul className={styles.customList}>

          {followers.map((follower, index) => (
            <div key={index}>
              <p>{follower.name}</p>
              <ListItem
                isRequest={false}
                isPost={false}
                isLike={false}
                isFollowerList={profileId ? false : isFollowerList === "Following"}
                isUserList={false}
                user={follower}
                onRefresh={handleRefresh}
              />
            </div>
          ))}
        </ul>
      )}
    </Modal>
  );
};



