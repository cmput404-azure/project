import "@fortawesome/fontawesome-free/css/all.min.css";

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { useEffect, useState } from "react";

import Alert from '@mui/material/Alert';
import { ContentType } from "../../models/modelTypes";
import { PostData as Post } from "../../models/models";
import ProfileService from "../../service/profile";
import ReactMarkdown from 'react-markdown';
import Snackbar from '@mui/material/Snackbar';
import Tooltip from '@mui/material/Tooltip';
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import follow from "../../service/follow";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";
import profileService from "../../service/profile";
import remarkGfm from 'remark-gfm';
import styles from "./PostCard.module.scss";
import { useAuth } from "../../state";
import { useNavigate } from 'react-router-dom';

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
  const authProvider = useAuth();
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [likeCount, setLikeCount] = useState<number>(Array.isArray(post.likes) ? 0 : post.likes.count);
  const [commentCount, setCommentCount] = useState<number>(Array.isArray(post.comments) ? 0 : post.comments.count);
  const [hasLiked, setHasLiked] = useState<boolean>(Array.isArray(post.likes)
    ? false
    : authProvider.user && post.likes.src.some((like) => like.author.id.split('/').pop() === authProvider.user.uuid)
  );
  const [imageSrc, setImageSrc] = useState<string>('');
  const navigate = useNavigate();
  const [shareDialogOpen, setShareDialogOpen] = useState<boolean>(false);
  const [isAuthor, setIsAuthor] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLiking, setIsLiking] = useState<boolean>(false);

  // Function to open the dialog
  const handleClickShare = () => {
    if (authProvider.user) {
      setShareDialogOpen(true);
    } 
    else {
      navigate('/login');
    }
  };

  useEffect(() => {
    const getUser = async () => {
      if (!authProvider.user) {
        return;
      }

      const currentUser = await ProfileService.fetchAuthorData(authProvider.user.uuid);
      if (post.author.id === currentUser.id) {
        setIsAuthor(true);
      } else if (authProvider.user.is_staff) {
        setIsAdmin(true);
      }
    }
    getUser();
  }, [])

  // Function to confirm sharing
  const handleConfirmShare = async () => {
    setShareDialogOpen(false)
    // Get followers and share the post
    const currentUser = await profileService.fetchAuthorData(authProvider.user.uuid)
    const share_obj = {
      type: "share",
      user: currentUser.id,
      post: post.id,
    }
    const followers = await follow.getFollowers(authProvider.user.uuid);
    for (const follower of followers) {
      await inbox.sendPostToInbox(follower.id, share_obj);
    }
  };

  const handleCloseShare = () => {
    setShareDialogOpen(false);
  };

  const handleClickLike = async () => {
    if (!authProvider.user) {
      navigate('/login');
      return;
    }

    if (hasLiked || isLiking) 
      return;

    setIsLiking(true);

    try {
      const currentUser = await api.get(`/api/authors/${authProvider.user.uuid}/`);
      const like_obj =  {
        type: "like",
        author: currentUser.data,
        published: new Date(post.published).toISOString(),
        object: post.id
      };
  
      await inbox.sendPostToInbox(post.author.id, like_obj);
      setLikeCount(likeCount + 1);
      setHasLiked(true);
    } catch (error) {
      console.error("Error liking post:", error);
    } finally {
      setIsLiking(false); 
    }
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
    const isExternalLink = !post.author.host.includes(window.location.hostname);

    if (isExternalLink) {
      // Later when able to connect to other nodes, fetch the remote author info using FQID
      // Then display the remote user info in our layout
    } else {
      const authorURL = `/authors/${extractUUID(post.author.id)}`;
      navigate(authorURL);
    }
  };

  useEffect(() => {
    const fetchImage = async () => {
      if (post.contentType === ContentType.MARKDOWN) {
        const imageRegex = /!\[.*?\]\((.*?)\)/; // Regex to find the image URL in the Markdown
        const match = post.content.match(imageRegex);
        if (match) {
          const imageUrl = match[1]; // Get the URL from the Markdown

          // Check if the imageUrl is a data URL
          if (imageUrl.startsWith("data:")) {
            // Directly set the src to the data URL
            setImageSrc(imageUrl);
          } else {
            // If it's not a data URL, fetch from the endpoint
            try {
              const response = await fetch(imageUrl);
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
            profileService.getProfilePicture(post.author)
          }
          alt={`${post.author.displayName}'s profile`}
          onClick={redirectToAuthorProfile}
        />
        <div className={styles.headerText}>
          <span className={styles.userName} onClick={redirectToAuthorProfile}>{post.author.displayName}</span>
          <span className={styles.postTime}>{new Date(post.published).toLocaleString()}</span>
        </div>

        <div className={styles.icon}>
          {normalizeVisibility(post.visibility) === 3 || isAuthor || isAdmin || normalizeVisibility(post.visibility) === 1 ? ( // friend post doesnt have a link 
            <Tooltip title="copy link">
              <i className="fas fa-link" onClick={handleGetLink}></i>
            </Tooltip>
          ) : null}
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
              }}
            >
              <i className="fas fa-heart icon" onClick={handleClickLike}></i>
              <span>{formatCount(likeCount)}</span>
            </div>
            <div className={styles.icon} onClick={onCommentButtonClick}>
              <i className="fas fa-comment"></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
          {normalizeVisibility(post.visibility) === 1 ? (
            <div className={styles.icon} onClick={handleClickShare}>
              <i className="fas fa-share"></i>
            </div>
          ) : null}
          <Dialog 
            open={shareDialogOpen} 
            onClose={handleCloseShare}
            sx={{
              '& .MuiDialog-paper': {
                backgroundColor: 'rgb(123, 123, 123)', 
                color: 'white',  
              },
            }}>
              <DialogTitle>Share Post</DialogTitle>
              <DialogContent>
                <DialogContentText sx={{ color: 'white' }}>
                  Do you want to share this post with all your friends and followers?
              </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button 
                  onClick={handleCloseShare} 
                  sx={{
                    backgroundColor: 'lightcoral',  
                    color: 'white',
                    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.2)',
                    '&:hover': {
                      backgroundColor: '#e57373',  
                    },
                  }}
                  autoFocus
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleConfirmShare} 
                  sx={{
                    backgroundColor: '#5acc8c', 
                    color: 'white',
                    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.2)',
                    '&:hover': {
                      backgroundColor: '#4ba578', 
                    },
                  }}
                  autoFocus
                >
                  Share
                </Button>
              </DialogActions>
          </Dialog>
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
                      <div className={styles.imgContainer}>
                        <img 
                          src={transformImageUri(src, alt, title)} 
                          alt={alt} 
                          title={title} 
                        />
                      </div>
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
