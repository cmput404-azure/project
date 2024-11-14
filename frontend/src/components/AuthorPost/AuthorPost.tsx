import React from 'react';
import styles from './AuthorPost.module.scss';
import { Author } from '../../models/models';
import { useAuth } from '../../state';
import InboxService from '../../service/inbox';
import { api } from '../../service/config';

interface AuthorPostProps {
  author: Author;
}

const AuthorPost: React.FC<AuthorPostProps> = ({ author }) => {
  const authProvider = useAuth();

  const handleAddButton = async () => {
    const userResponse = await api.get<Author>(`/api/authors/${authProvider.user.uuid}/`);
    const myInfo = userResponse.data;

    const followRequest = {
      type: "follow",
      summary: `${myInfo.username} wants to follow ${author.username}`,
      actor: { // person who sends the request
        type: "author",
        id: `${myInfo.id}`,
        host: `${myInfo.host}`,
        displayName: `${myInfo.displayName}`,
        username: `${myInfo.username}`,
        bio: `${myInfo.bio}`,
        profileImage: `${myInfo.profileImage}`,
        github: `${myInfo.github}`,
        page: `${myInfo.page}`,
      },
      object: { // person who the request is being sent to
        type: "author",
        id: `${author.id}`,
        host: `${author.host}`,
        displayName: `${author.displayName}`,
        username: `${author.username}`,
        bio: `${author.bio}`,
        profileImage: `${author.profileImage}`,
        github: `${author.github}`,
        page: `${author.page}`,
      }
    };
  
    await InboxService.sendPostToInbox(author.id, followRequest);
  }

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
        <button className={styles['add-button']} onClick={handleAddButton}>
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


