// @ts-nocheck
import React, { useEffect, useState } from 'react';
import axios, { get } from 'axios';
import follow, { getFollowers, getFollowing, getFriends } from "../../service/follow";

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
}

Modal.setAppElement('#root');

export default function FollowList({ isOpen, onClose, isFollowerList}: FollowerListProps) {
  const [followers, setFollowers] = useState<Follower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
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
  }, [isOpen]);

  const fetchFriends = async () => {
    try {
      const data = await follow.getFriends(authProvider.user.uuid);
      setFollowers(data);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);

    }
  };


  const fetchFollowers = async () => {
    try {
      const data = await follow.getFollowers(authProvider.user.uuid);
      setFollowers(data);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);
    }
  };

  const fetchFollowing = async () => {
    try {
      const data = await follow.getFollowing(authProvider.user.uuid);
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
      <button onClick={onClose} style={{ float: 'right' }}>Close</button>
      <h2 className={styles.h2}>{isFollowerList}</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <ul className={styles.ul}>

          {followers.map((follower, index) => (
            <div key={index}>
              <p>{follower.name}</p> 
              <ListItem
                isRequest={false}
                isPost={false}
                isLike={false}
                isFollowerList={isFollowerList === "Following"}
                isUserList={false}
                user={follower}
              />
            </div>
          ))}
        </ul>
      )}
    </Modal>
  );
};



