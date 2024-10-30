import "@fortawesome/fontawesome-free/css/all.min.css";

import { Alert, Snackbar, Tooltip } from '@mui/material';
import { useEffect, useState } from "react";

import { ContentType } from "../../models/modelTypes";
import { PostData as PostModel } from "../../models/models";
import follow from "../../service/follow";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import postService from "../../service/post";
import styles from "./Post.module.scss";
import { useAuth } from "../../state";
import { useParams } from "react-router";

export default function Post() {
   const { postID } = useParams<{ postID: string }>();
   const authProvider = useAuth();

   const [post, setPost] = useState<PostModel | null>(null);
   const [likeCount, setLikeCount] = useState(0);
   const [commentCount, setCommentCount] = useState(0);
   const [hasLiked, setHasLiked] = useState(false);
   const [hasShared, setHasShared] = useState(false);
   const [openSnackbar, setOpenSnackbar] = useState(false);
   const [isCommentOpen, setIsCommentOpen] = useState(false);

   useEffect(() => {
      const fetchPost = async () => {
         try {
            if (postID) {
               const postData = await postService.getPost(`api/posts/${postID}`);
               setPost(postData);
               setLikeCount(postData.likes.length);
               setCommentCount(postData.comments.length);
            }
         } catch (error) {
            console.error("Error fetching post data:", error);
         }
      };
      fetchPost();
   }, [postID]);

   const handleToggleComment = () => setIsCommentOpen(!isCommentOpen);

   const handleSharePost = async () => {
      if (!post || hasShared) return;

      const followers = await follow.getFollowers(authProvider.user.uuid);
      const friends = await follow.getFriends(authProvider.user.uuid);
      const recipients = post.visibility === 1 || post.visibility === 3 ? followers : friends;

      await Promise.all(recipients.map(({ id }) => inbox.sendPostToInbox(id, post)));
      setHasShared(true);
   };

   const handleLikePost = async () => {
      if (!post || hasLiked) return;

      const likeObj = {
         type: "like",
         author: post.author,
         published: new Date(post.published).toISOString(),
         object: post.id,
      };

      const recipients = post.visibility === 1 || post.visibility === 3
         ? await follow.getFollowers(authProvider.user.uuid)
         : await follow.getFriends(authProvider.user.uuid);

      await Promise.all(recipients.map(({ id }) => inbox.sendPostToInbox(id, likeObj)));
      setLikeCount((count) => count + 1);
      setHasLiked(true);
   };

   const handleCopyLink = () => {
      if (post) {
         navigator.clipboard.writeText(post.id).then(
            () => setOpenSnackbar(true),
            (err) => console.error('Could not copy link: ', err)
         );
      }
   };

   const handleCloseSnackbar = (event?: React.SyntheticEvent | Event, reason?: string) => {
      if (reason !== 'clickaway') setOpenSnackbar(false);
   };

   if (!post) return <div>Loading...</div>;

   return (
      <div className={styles.card}>
         <div className={styles.grid}>
            <img
               className={styles.profilePic}
               src={post.author.profileImage ?? `https://ui-avatars.com/api/?background=random&name=${post.author.displayName}`}
               alt={`${post.author.displayName}'s profile`}
            />
            <div className={styles.headerText}>
               <span className={styles.userName}>{post.author.displayName}</span>
               <span className={styles.postTime}>{new Date(post.published).toLocaleString()}</span>
            </div>
            <Tooltip title="Copy link">
               <i className="fas fa-link" onClick={handleCopyLink}></i>
            </Tooltip>
            <Snackbar
               open={openSnackbar}
               autoHideDuration={2000}
               onClose={handleCloseSnackbar}
               anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
               <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
                  Link copied to clipboard!
               </Alert>
            </Snackbar>
            <div className={styles.cardFooter}>
               <div className={styles.essentials}>
                  <div
                     className={`${styles.icon} ${hasLiked ? styles.liked : ""}`}
                     onClick={(e) => {
                        e.stopPropagation();
                        handleLikePost();
                     }}
                  >
                     <i className="fas fa-heart icon"></i>
                     <span>{formatCount(likeCount)}</span>
                  </div>
                  <div className={styles.icon} onClick={handleToggleComment}>
                     <i className="fas fa-comment"></i>
                     <span>{formatCount(commentCount)}</span>
                  </div>
               </div>
               <div className={`${styles.icon} ${hasShared ? styles.shared : ""}`} onClick={handleSharePost}>
                  <i className="fas fa-share"></i>
               </div>
            </div>
            <div className={styles.cardContent}>
               <div className={styles.postTitle}>{post.title}</div>
               {post.contentType !== ContentType.MARKDOWN && post.contentType !== ContentType.PLAIN ? (
                  <div className={styles.imgContainer}>
                     <img className={styles.postImage} src={post.content} alt={post.description} />
                  </div>
               ) : (
                  <div className={styles.postText}>{post.content}</div>
               )}
            </div>
         </div>
         {isCommentOpen && <div>Comment section here</div>}
      </div>
   );
}