import React from 'react';
import styles from './AuthorPost.module.scss';

interface AuthorPostProps {
  authorImage: string;
  authorName: string;
  userName: string;
  postText: string;
  onAddClick: () => void;
}

const AuthorPost: React.FC<AuthorPostProps> = ({ authorImage, authorName, userName, postText, onAddClick }) => {
  return (
    <div className={styles['author-post']}>
      <div className={styles['post-header']}>
        <div className={styles['author-info']}>
          <img src={authorImage} alt="Author" className={styles['author-avatar']} />
          <div>
            <h3>{authorName}</h3>
            <p>@{userName}</p>
          </div>
        </div>
        <button className={styles['add-button']} onClick={onAddClick}>
          <span>+</span>
        </button>
      </div>
      <div className={styles['post-content']}>
        <p>{postText}</p>
      </div>
    </div>
  );
};

export default AuthorPost;


