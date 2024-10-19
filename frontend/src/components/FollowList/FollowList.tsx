// @ts-nocheck
import React, { useEffect, useState } from 'react';

import ListItem from '../ListItem/ListItem';
import Modal from 'react-modal';
import axios from 'axios';
import styles from './FollowList.module.scss';

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
  isFollowerList: boolean; // true --> followerlist, false --> followingList
}


interface FollowerResponse {
  followers: Follower[];
}

Modal.setAppElement('#root');

export default function FollowList({ isOpen, onClose, isFollowerList }: FollowerListProps) {
  const [followers, setFollowers] = useState<Follower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (isFollowerList === true) {
        fetchFollowers(); // Fetch followers only when the modal is open
        return;
      } else {
        fetchFollowing();
      }
    }
  }, [isOpen]);

  const fetchFollowers = async () => {
    try {
      const response = await axios.get<FollowerResponse>(`http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/followers/`, {
      });

      const data = response.data;
      setFollowers(response.data.followers);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);

    }
  };

  const fetchFollowing = async () => {
    if (isFollowerList === false) {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/authors/eba591e5-91a3-4b80-9fe4-cd3eb8b4b544/following/`, {
          params: {
            action: 'following'
          }
        });

        const data = response.data;
        setFollowers(response.data.followers);
        setLoading(false);
      } catch (error) {
        console.error('Fetch error:', error);
        setLoading(false);

      }
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onClose}
      contentLabel="Follower List"
      style={{
        content: { width: '400px', margin: 'auto', padding: '20px', borderRadius: '10px' },
        overlay: { backgroundColor: 'rgba(0, 0, 0, 0.5)' }
      }}
    >
      <button onClick={onClose} style={{ float: 'right' }}>Close</button>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <ul className={styles.ul}>
          {followers.map((follower, index) =>
            isFollowerList ? (
              <ListItem
                key={index}
                isRequest={false}
                isPost={false}
                isLike={false}
                isFollowerList={false}
                isUserList={false}
                user={follower}
              />
            ) : (
              <ListItem
                key={index}
                isRequest={false}
                isPost={false}
                isLike={false}
                isFollowerList={true}
                isUserList={false}
                user={follower}
              />
            )
          )}
        </ul>
      )}
    </Modal>
  );
};



