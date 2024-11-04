import "@fortawesome/fontawesome-free/css/all.min.css";

import { Alert, CircularProgress, Snackbar, Tooltip } from "@mui/material";
import { useEffect, useState } from "react";
import { decodeBase64ToUrl } from "../../util/rendering/decodeBase64ToUrl";

import CommentInputField from "../CommentInput/CommentInput";
import { ContentType } from "../../models/modelTypes";
import { PostData as PostModel } from "../../models/models";
import follow from "../../service/follow";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import postService from "../../service/post";
import FollowService from "../../service/follow";
import ProfileService from "../../service/profile";
import styles from "./Post.module.scss";
import { useAuth } from "../../state";
import { useNavigate, useParams } from "react-router";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../../service/config";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Button,
} from "@mui/material";
import profileService from "../../service/profile";
import { PostData } from "../../models/models";

export default function Post({
  postGiven,
  canToggleComments = true,
}: {
  postGiven?: PostModel;
  canToggleComments?: boolean;
}) {
  const { postID: postIDFromParams } = useParams<{ postID: string }>();
  const postID = postGiven ? postGiven.id : postIDFromParams;

  const authProvider = useAuth();

  const [post, setPost] = useState<PostModel | null>(null);
  const [likeCount, setLikeCount] = useState(0);
  const [commentCount, setCommentCount] = useState(0);
  const [hasLiked, setHasLiked] = useState(false);
  const [hasShared, setHasShared] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isCommentOpen, setIsCommentOpen] = useState(false);
  const [commentList, setCommentList] = useState<any[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const navigate = useNavigate();
  const [imageSrc, setImageSrc] = useState<string>("");

  useEffect(() => {
    const fetchPost = async () => {
      try {
        if (postID) {
          const postData = await postService.getPost(`api/posts/${postID}`);
          // put the post data into a list to be able to decode it
          let postDataList = [];
          postDataList.push(postData);
          // decode base64 content
          const decodedPost = decodeBase64ToUrl(postDataList);
          postData.content = decodedPost[0].content;

          const authUser = await ProfileService.fetchAuthorData(
            authProvider.user.uuid
          );
          const url = `${authUser.host}authors/${authProvider.user.uuid}`;

          if (url !== postData.author.id) {
            let authorId = postData.author.id
              .replace(/\/+$/, "")
              .split("/")
              .pop();
            const encodedUrl = encodeURIComponent(url);
            const is_following = await FollowService.checkFollowing(
              authorId,
              encodedUrl
            );
            if (!is_following) {
              setOpenSnackbar(true);
              setShowAlert(true);
              setTimeout(() => {
                navigate("/home");
              }, 2000);
            }
          }

          setPost(postData);
          setHasLiked(
            postData.likes.src.some((like) =>
              like.object.includes(authProvider.user.uuid)
            )
          );
          setCommentList(postData.comments.src.reverse());
          setLikeCount(
            Array.isArray(postData.likes) ? 0 : postData.likes.count
          );
          setCommentCount(
            Array.isArray(postData.comments) ? 0 : postData.comments.count
          );
        }
      } catch (error) {
        if (error.response && error.response.status === 403) {
          navigate("/login");
        } else {
          console.error("Error fetching post data:", error);
        }
      }
    };
    fetchPost();
  }, [postID, authProvider.user.uuid, navigate]);

  const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src;
  };

  const handleToggleComment = () => setIsCommentOpen(!isCommentOpen);

  const handleNewComment = (newComment) => {
    const newCommentList = [...commentList, newComment];
    setCommentList(newCommentList);
  };

  const handleSharePost = async () => {
    if (!post || hasShared) return;

    setIsShareDialogOpen(true);

    const followers = await follow.getFollowers(authProvider.user.uuid);
    const friends = await follow.getFriends(authProvider.user.uuid);
    const recipients =
      post.visibility === 1 || post.visibility === 3 ? followers : friends;

    await Promise.all(
      recipients.map(({ id }) => inbox.sendPostToInbox(id, post))
    );
    setHasShared(true);
  };

  const handleLikePost = async () => {
    if (!authProvider.user) {
      navigate("/login");
      return;
    }

    if (hasLiked) return;

    try {
      const currentUser = await api.get(
        `/api/authors/${authProvider.user.uuid}/`
      );
      const like_obj = {
        type: "like",
        author: currentUser.data,
        published: new Date(post.published).toISOString(),
        object: post.id,
      };

      await inbox.sendPostToInbox(post.author.id, like_obj);
      setLikeCount(likeCount + 1);
      setHasLiked(true);
    } catch (error) {
      console.error("Error liking post:", error);
    }
  };

  const handleCopyLink = () => {
    if (post) {
      const domain = window.location.host;
      const postId = post.id.split("/").pop();
      const path = `/#/post/${postId}`;

      const link = `${domain}${path}`;
      navigator.clipboard.writeText(link).then(
        () => setOpenSnackbar(true),
        (err) => console.error("Could not copy link: ", err)
      );
    }
  };

  const handleCloseSnackbar = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason !== "clickaway") setOpenSnackbar(false);
  };

  if (!post)
    return (
      <div>
        <CircularProgress sx={{ color: "#70ffaf" }} />
      </div>
    );

  return showAlert ? (
    <Snackbar
      open={openSnackbar}
      autoHideDuration={2000}
      onClose={handleCloseSnackbar}
      anchorOrigin={{ vertical: "top", horizontal: "right" }}
    >
      <Alert
        onClose={handleCloseSnackbar}
        severity="info"
        sx={{ width: "100%" }}
      >
        Sorry, this post has been hidden from you.
      </Alert>
    </Snackbar>
  ) : (
    <div className={styles.card}>
      <div className={styles.grid}>
        <img
          className={styles.profilePic}
          src={
            post.author.profileImage ??
            `https://ui-avatars.com/api/?background=random&name=${post.author.displayName}`
          }
          alt={`${post.author.displayName}'s profile`}
        />
        <div className={styles.headerText}>
          <span className={styles.userName}>{post.author.displayName}</span>
          <span className={styles.postTime}>
            {new Date(post.published).toLocaleString()}
          </span>
        </div>
        <Tooltip title="Copy link">
          <i className="fas fa-link" onClick={handleCopyLink}></i>
        </Tooltip>

        <Snackbar
          open={openSnackbar}
          autoHideDuration={2000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity="success"
            sx={{ width: "100%" }}
          >
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
            <div
              className={styles.icon}
              onClick={canToggleComments ? handleToggleComment : null}
            >
              <i className="fas fa-comment"></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
          {post.visibility === 1 ? (
            <div
              className={`${styles.icon} ${hasShared ? styles.shared : ""}`}
              onClick={handleSharePost}
            >
              <i className="fas fa-share"></i>
            </div>
          ) : null}
          <ShareDialogue post={post} isDialogOpen={isShareDialogOpen} />
        </div>
        <div className={styles.cardContent}>
          <div className={styles.postTitle}>{post.title}</div>
          {post.contentType !== ContentType.MARKDOWN &&
          post.contentType !== ContentType.PLAIN ? (
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
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    img: ({ src, alt, title }) => {
                      return (
                        <img
                          src={transformImageUri(src, alt, title)}
                          alt={alt}
                          title={title}
                        />
                      );
                    },
                  }}
                >
                  {post.content}
                </ReactMarkdown>
              ) : (
                post.content
              )}
            </div>
          )}
        </div>
      </div>

      {isCommentOpen && canToggleComments ? (
        <div className={styles.comments}>
          <div className={styles.commentsHeader}>Comments</div>
          <CommentInputField
            authorObj={post.author}
            post={post}
            onCommentAdded={handleNewComment}
          />
          {commentList.map((comment) => (
            <div key={comment.id} className={styles.comment}>
              <div key={comment.id} className={styles.comment}>
                <img
                  src={
                    post.author.profileImage
                      ? post.author.profileImage
                      : `https://ui-avatars.com/api/?background=random&name=${comment.author.displayName}`
                  }
                  className={styles.userImage}
                />
              </div>
              <div className={styles.commentContent}>
                <div className={styles.authorTime}>
                  <div className={styles.commentAuthor}>
                    {comment.author.displayName}
                  </div>
                  <div className={styles.timePosted}>{comment.published}</div>
                </div>
                <div className={styles.commentText}>{comment.comment}</div>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

interface ShareDialogueProps {
  post: PostData;
  isDialogOpen: boolean;
}

function ShareDialogue({ post, isDialogOpen }: ShareDialogueProps) {
  const [shareDialogOpen, setShareDialogOpen] = useState<boolean>(isDialogOpen);
  const authProvider = useAuth();

  // Update shareDialogOpen when isDialogOpen prop changes
  useEffect(() => {
    setShareDialogOpen(isDialogOpen);
  }, [isDialogOpen]);

  const handleCloseShare = () => {
    setShareDialogOpen(false);
  };

  // Function to confirm sharing
  const handleConfirmShare = async () => {
    setShareDialogOpen(false);
    // Get followers and share the post
    const currentUser = await profileService.fetchAuthorData(
      authProvider.user.uuid
    );
    const share_obj = {
      type: "share",
      user: currentUser.id,
      post: post.id,
    };
    const followers = await follow.getFollowers(authProvider.user.uuid);
    for (const follower of followers) {
      await inbox.sendPostToInbox(follower.id, share_obj);
    }
    console.log("Post shared with followers");
  };

  return (
    <Dialog
      open={shareDialogOpen}
      onClose={handleCloseShare}
      sx={{
        "& .MuiDialog-paper": {
          backgroundColor: "rgb(123, 123, 123)",
          color: "white",
        },
      }}
    >
      <DialogTitle>Share Post</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ color: "white" }}>
          Do you want to share this post with all your friends and followers?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={handleCloseShare}
          sx={{
            backgroundColor: "lightcoral",
            color: "white",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.2)",
            "&:hover": {
              backgroundColor: "#e57373",
            },
          }}
          autoFocus
        >
          Cancel
        </Button>
        <Button
          onClick={handleConfirmShare}
          sx={{
            backgroundColor: "#5acc8c",
            color: "white",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.2)",
            "&:hover": {
              backgroundColor: "#4ba578",
            },
          }}
          autoFocus
        >
          Share
        </Button>
      </DialogActions>
    </Dialog>
  );
}
