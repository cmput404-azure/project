// @ts-nocheck
import React, { useEffect, useState } from 'react';
import ListItem from '../ListItem/ListItem';
import Modal from 'react-modal';
import axios from 'axios';
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


interface FollowerResponse {
  followers: Follower[];
}

Modal.setAppElement('#root');

export default function FollowList({ isOpen, onClose, isFollowerList }: FollowerListProps) {
  const [followers, setFollowers] = useState<Follower[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const authProvider = useAuth();

  axios.defaults.withCredentials = true;
  axios.defaults.xsrfCookieName = "csrftoken";
  axios.defaults.xsrfHeaderName = "x-csrftoken";

  useEffect(() => {
    if (isOpen) {
      if (isFollowerList === 'follower') {
        fetchFollowers(); // Fetch followers only when the modal is open
        return;
      } else if (isFollowerList === 'following') {
        fetchFollowing();
      }else{
        fetchFriends();
      }
    }
  }, [isOpen]);

  const fetchFriends = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/following/`, {
        params: {
          action: 'friends'
        }
      });
      const data = response.data;
      setFollowers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);

    }
  };


  const fetchFollowers = async () => {
    try {
      const response = await axios.get<FollowerResponse>(`http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/followers/`, {
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
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/following/`, {
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



