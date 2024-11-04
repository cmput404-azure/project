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
  const [commentList, setCommentList] = useState<any[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const navigate = useNavigate();
  const [imageSrc, setImageSrc] = useState<string>("");

  useEffect(() => {
    const fetchPost = async () => {
      try {
        if (postID) {
          const postData = await postService.getPost(`api/posts/${postID}`);
          console.log("Post Data:", postData);
          console.log("Post Data Author:", postData.author);
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
          setCommentList(postData.comments.src.reverse());
          console.log("Comment List:", commentList);
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

  useEffect(() => {
    const fetchImage = async () => {
      if (post && post.contentType === ContentType.MARKDOWN) {
        const imageRegex = /!\[.*?\]\((.*?)\)/;
        const match = post.content.match(imageRegex);
        if (match) {
          const imageUrl = match[1];
          console.log("Image URL:", imageUrl);

          if (imageUrl.startsWith("data:")) {
            setImageSrc(imageUrl);
          } else {
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
  }, [post]); // Only runs if post changes

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
    if (!post || hasLiked) return;

    const likeObj = {
      type: "like",
      author: post.author,
      published: new Date(post.published).toISOString(),
      object: post.id,
    };

    const recipients =
      post.visibility === 1 || post.visibility === 3
        ? await follow.getFollowers(authProvider.user.uuid)
        : await follow.getFriends(authProvider.user.uuid);

    await Promise.all(
      recipients.map(({ id }) => inbox.sendPostToInbox(id, likeObj))
    );
    setLikeCount((count) => count + 1);
    setHasLiked(true);
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
            <div className={styles.icon} onClick={handleToggleComment}>
              <i className="fas fa-comment"></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
          <div
            className={`${styles.icon} ${hasShared ? styles.shared : ""}`}
            onClick={handleSharePost}
          >
            <i className="fas fa-share"></i>
          </div>
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

      {isCommentOpen ? (
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
