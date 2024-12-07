import React, { useState }  from 'react';

import AddIcon from '@mui/icons-material/Add';
import { Author } from '../../models/models';
import { Avatar } from "@mui/material";
import InboxService from '../../service/inbox';
import { extractHost } from "../../util/formatting/extractHost";
import profileService from "../../service/profile";
import styles from './AuthorPost.module.scss';
import { useAuth } from '../../state';
import { useNavigate } from 'react-router';

interface AuthorPostProps {
  author: Author;
}

const AuthorPost: React.FC<AuthorPostProps> = ({ author }) => {
  const authProvider = useAuth();
  const navigate = useNavigate();
  const [isRequested, setIsRequested] = useState(false);

  const redirectToAuthorProfile = () => {
    const encodedId = encodeURIComponent(author.id);
    const authorURL = `/authors/${encodedId}`;
    navigate(authorURL);
  };
  
  const handleAddButton = async () => {
    const userResponse = await profileService.fetchAuthorData(authProvider.user.uuid);

    const followRequest = {
      type: "follow",
      summary: `${userResponse.username} wants to follow ${author.displayName}`,
      actor: { // person who sends the request
        type: "author",
        id: `${userResponse.id}`,
        host: `${userResponse.host}`,
        displayName: `${userResponse.displayName}`,
        username: userResponse.username || "",
        bio: userResponse.bio || "",
        profileImage: `${userResponse.profileImage}`,
        github: `${userResponse.github}`,
        page: `${userResponse.page}`,
      },
      object: { // person who the request is being sent to
        type: "author",
        id: `${author.id}`,
        host: `${author.host}`,
        displayName: `${author.displayName}`,
        username: author.username || "",
        bio: author.bio || "",
        profileImage: `${author.profileImage}`,
        github: `${author.github}`,
        page: `${author.page}`,
      }
    };
  
    const status = await InboxService.sendPostToInbox(author.id, followRequest);
    if (status === 200 || status === 201) {
      setIsRequested(true); // Change button state on success
    }
  }

  return (
    <div className={styles.author_post}>
      <div className={styles.post_header}>
        <div className={styles.author_info}>
          <Avatar
            src={profileService.getProfilePicture(author)}
            alt="Author"
            onClick={redirectToAuthorProfile}
            className={styles.author_avatar}
          />
          <div>
            <h3 onClick={redirectToAuthorProfile}>{author.displayName}</h3>
            <p>@{author.username ?? extractHost(author.host)}</p>
          </div>
        </div>
        <button
          className={`${styles.add_button} ${isRequested ? styles.add_button__requested : ''}`}
          onClick={handleAddButton}
          disabled={isRequested}
        >
          {isRequested ? 'Requested' : (<AddIcon/>)}
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


