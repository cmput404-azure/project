import React from 'react';
import styles from './AuthorPost.module.scss';
import { Author } from '../../models/models';

interface AuthorPostProps {
  author: Author;
}

const AuthorPost: React.FC<AuthorPostProps> = ({ author }) => {
  return (
    <div className={styles['author-post']}>
      <div className={styles['post-header']}>
        <div className={styles['author-info']}>
          <img src={
            author.profileImage && author.profileImage.trim() !== "" ?
            author.profileImage :
            `https://ui-avatars.com/api/?background=random&name=${author.displayName}`
          } alt="Author" className={styles['author-avatar']} />
          <div>
            <h3>{author.displayName}</h3>
            <p>@{author.username}</p>
          </div>
        </div>
        <button className={styles['add-button']}>
          <span>+</span>
        </button>
      </div>
      <div className={styles['post-content']}>
        <p>{author.bio}</p>
      </div>
    </div>
  );
};

export default AuthorPost;


