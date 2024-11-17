import React, { useState }  from 'react';
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
  const [isRequested, setIsRequested] = useState(false); 
  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };
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
  
    const status = await InboxService.sendPostToInbox(author.id, followRequest);
    if (status === 200) {
      setIsRequested(true); // Change button state on success
    }
  }

  return (
    <div className={styles.author_post}>
      <div className={styles.post_header}>
        <div className={styles.author_info}>
          <img
            src={
              author.profileImage && author.profileImage.trim() !== ""
                ? author.profileImage
                : `https://ui-avatars.com/api/?background=random&name=${author.displayName}`
            }
            alt="Author"
            className={styles.author_avatar}
          />
          <div>
            <h3>{author.displayName}</h3>
            <p>@{author.username}</p>
          </div>
        </div>
        <button
          className={`${styles.add_button} ${isRequested ? styles.add_button__requested : ''}`}
          onClick={handleAddButton}
          disabled={isRequested}
        >
          {isRequested ? 'Requested' : '+'}
        </button>
      </div>
      {author.bio && author.bio.trim() !== "" && (
        <div className={styles.post_content}>
          <p>{author.bio}</p>
        </div>
      )}
    </div>
  );  
};

export default AuthorPost;


