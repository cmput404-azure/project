import "@fortawesome/fontawesome-free/css/all.min.css";
import Alert from '@mui/material/Alert';
import { ContentType } from "../../models/modelTypes";
import { PostData as Post } from "../../models/models";
import Snackbar from '@mui/material/Snackbar';
import Tooltip from '@mui/material/Tooltip';
import follow from "../../service/follow";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import styles from "./PostCard.module.scss";
import { useAuth } from "../../state";
import { Author,  Follower } from "../../models/models";
import { useState, useEffect } from "react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { api } from "../../service/config";

interface PostCardProps {
  post: Post
  onCommentButtonClick?: () => void; // optional
  onClick?: () => void;
}

function PostCard({
  post,
  onCommentButtonClick,
  onClick,
}: PostCardProps) {
  const [open, setOpen] = useState<boolean>(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [likeCount, setLikeCount] = useState<number>(post.likes.length);
  const [commentCount, setCommentCount] = useState<number>(post.comments.length);
  const [hasLiked, setHasLiked] = useState<boolean>(false);
  const [hasShared, setHasShared] = useState<boolean>(false);
  const [imageSrc, setImageSrc] = useState<string>('');

  const authProvider = useAuth();

  const handleClickShare = async () => {
    if (hasShared) return;

    // Get friends and followers list, followers inlcude both friends and followers
    const followers = await follow.getFollowers(authProvider.user.uuid);
    const friends = await follow.getFriends(authProvider.user.uuid);

    // send to followers if post is public or unlisted
    // always send to friends for all type of posts
    if (post.visibility === 1 || post.visibility === 3) {
      for (const follower of followers) {
        const inboxResponse = await inbox.sendPostToInbox(follower.id, post);
      }
    } else {
      for (const friend of friends) {
        const inboxResponse = await inbox.sendPostToInbox(friend.id, post);
      }
    }

    setHasShared(true);
  };

  const handleClickLike = async () => {
    if (hasLiked) return;
    console.log(authProvider.user.uuid);
    const currentUser = await api.get(`/api/authors/${authProvider.user.uuid}/`);
    const like_obj =  {
      type: "like",
      author: currentUser.data,
      published: new Date(post.published).toISOString(),
      object: post.id
    }
  
    const inboxResponse = await inbox.sendPostToInbox(post.author.id, like_obj);

    // Get friends and followers list, followers inlcude both friends and followers
    // const followers = await follow.getFollowers(authProvider.user.uuid);
    // const friends =  await follow.getFriends(authProvider.user.uuid);

    // send to followers if post is public or unlisted
    // always send to friends for all type of posts

    // if (post_obj.visibility === 1 || post_obj.visibility === 3) {
    //   for (const follower of followers) {
    //     const inboxResponse = await inbox.sendPostToInbox(follower.id, like_obj);
    //   }
    // } else {
    //   for (const friend of friends) {
    //     const inboxResponse = await inbox.sendPostToInbox(friend.id, like_obj);
    //   }
    // } 

    setLikeCount(likeCount + 1);
    setHasLiked(true);
  };

  const handleGetLink = () => {
    const domain = window.location.host;
    const postId = post.id.split("/").pop();
    const path = `/#/post/${postId}`;

    const link = `${domain}${path}`;

    navigator.clipboard.writeText(link)
      .then(() => {
        setOpenSnackbar(true);
      })
      .catch(err => {
        console.error('Could not copy link: ', err);
      });
  };

  const handleCloseSnackbar = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  const redirectToAuthorProfile = () => {
    // right now this works locally, other teams might not have the same url format
    const localUserURL = `${post.author.host}/#/authors/${post.author.id}`;
    window.location.assign(localUserURL);

    // might need to add logic for remote users in the future
 };

  useEffect(() => {
    const fetchImage = async () => {
      if (post.contentType === ContentType.MARKDOWN) {
          const imageRegex = /!\[.*?\]\((.*?)\)/; // Regex to find the image URL in the Markdown
          const match = post.content.match(imageRegex);
          if (match) {
              const imageUrl = match[1]; // Get the URL from the Markdown
              console.log("imageURL: ", imageUrl);
              
              // Check if the imageUrl is a data URL
              if (imageUrl.startsWith("data:")) {
                  // Directly set the src to the data URL
                  setImageSrc(imageUrl);
              } else {
                  // If it's not a data URL, fetch from the endpoint
                  try {
                      const response = await fetch(imageUrl);
                      console.log(response);
                      if (response.ok) {
                          const jsonResponse = await response.json();
                          const imageData = jsonResponse.image;
                          setImageSrc(imageData);
                      } else {
                          console.error("Error fetching image:", response.statusText);
                      }
                  } catch (error) {
                      console.error("Error fetching image:", error);
                  }
              }
          }
      }
  };

    fetchImage();
}, [post.content, post.contentType]);

const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src; // Return the fetched Base64 string if available, otherwise the original src
};
 
  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.grid}>
        <img
          className={styles.profilePic}
          src={
            post.author.profileImage ??
            `https://ui-avatars.com/api/?background=random&name=${post.author.displayName}`
          }
          alt={`${post.author.displayName}'s profile`}
          onClick={redirectToAuthorProfile}
        />
        <div className={styles.headerText}>
          <span className={styles.userName} onClick={redirectToAuthorProfile}>{post.author.displayName}</span>
          <span className={styles.postTime}>{new Date(post.published).toLocaleString()}</span>
        </div>
        <div className={styles.icon}>
          <Tooltip title="copy link">
            <i className="fas fa-link" onClick={handleGetLink}></i>
          </Tooltip>
          <Snackbar
            open={openSnackbar}
            autoHideDuration={2000} // auto close after 2s
            onClose={handleCloseSnackbar}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
              Link copied to clipboard!
            </Alert>
          </Snackbar>
        </div>
        <div className={styles.cardFooter}>
          <div className={styles.essentials}>
            <div
              className={`${styles.icon} ${hasLiked ? styles.liked : ""}`}
              onClick={(e) => {
                e.stopPropagation();
                console.log("Like");
              }}
            >
              <i className="fas fa-heart icon" onClick={handleClickLike}></i>
              <span>{formatCount(likeCount)}</span>
            </div>
            <div className={styles.icon} onClick={onCommentButtonClick}>
              <i className="fas fa-comment"></i>
              <span>{formatCount(post.comments.length)}</span>
            </div>
          </div>
          <div className={`${styles.icon} ${hasShared ? styles.shared : ""}`} onClick={handleClickShare}>
            <i className="fas fa-share"></i>
          </div>
        </div>
        <div className={styles.cardContent}>
          <div className={styles.postTitle}>{post.title}</div>
          {(post.contentType !== ContentType.MARKDOWN && post.contentType !== ContentType.PLAIN) ? (
            <div className={styles.imgContainer}>
              <img
                className={styles.postImage}
                src={post.content}
                alt={post.description}
              />
            </div>
          ) : (
            // <div className={styles.postText}>{post.content}</div>
            <div className={styles.postText}>
              {post.contentType === ContentType.MARKDOWN ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                    img: ({ src, alt, title }) => {
                      return (
                          <img src={transformImageUri(src, alt, title)} alt={alt} title={title} />
                      );
                  }
                }}>
                      {post.content}
                  </ReactMarkdown>
              ) : (
                  post.content
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PostCard;
