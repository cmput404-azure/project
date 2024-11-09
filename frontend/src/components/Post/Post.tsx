import "@fortawesome/fontawesome-free/css/all.min.css";

import {
  Alert,
  CircularProgress,
  Snackbar,
  Tooltip,
  Modal,
} from "@mui/material";
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
import { extractUUID } from "../../util/formatting/extractUUID";
import Avatar from "@mui/material/Avatar";
import auth from "../../service/auth";

export default function Post({
  postGiven,
  canToggleComments = true,
  isModal = false,
}: {
  postGiven?: PostModel;
  canToggleComments?: boolean;
  isModal?: boolean;
}) {
  const { postID: postIDFromParams } = useParams<{ postID: string }>();
  const postID = postGiven ? null : postIDFromParams;

  const authProvider = useAuth();

  const [post, setPost] = useState<PostModel | null>(null);
  const [likeCount, setLikeCount] = useState(0);
  const [commentCount, setCommentCount] = useState(0);
  const [hasLiked, setHasLiked] = useState(false);
  // const [hasShared, setHasShared] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isCommentOpen, setIsCommentOpen] = useState(false);
  const [commentList, setCommentList] = useState<any[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const navigate = useNavigate();
  const [imageSrc, setImageSrc] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentAuthor, setCurrentAuthor] = useState<any>();

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
  
          if (authProvider.user) {
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
              if (!authProvider.user.is_staff) {
                if (postData.visibility !== 1) {
                  if (!is_following || postData.visibility === 2) {
                    setOpenSnackbar(true);
                    setShowAlert(true);
                    setTimeout(() => {
                      navigate("/home");
                    }, 2000);
                  }
                }
              }
            }
  
            setHasLiked(
              postData.likes.src.some((like) =>
                like.id.includes(authProvider.user.uuid)
              )
            );
          }

          console.log(postData);
          setPost(postData);
  
          setCommentList(postData.comments.src.reverse());
          setLikeCount(
            Array.isArray(postData.likes) ? 0 : postData.likes.count
          );
          setCommentCount(
            Array.isArray(postData.comments) ? 0 : postData.comments.count
          );
        } else {
          setPost(postGiven);
          setHasLiked(
            postGiven.likes.src.some((like) =>
              like.id.includes(authProvider.user.uuid)
            )
          );
          setCommentList(postGiven.comments.src.reverse());
          setLikeCount(
            Array.isArray(postGiven.likes) ? 0 : postGiven.likes.count
          );
          setCommentCount(
            Array.isArray(postGiven.comments) ? 0 : postGiven.comments.count
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
    const fetchAuthor = async () => {
      if (authProvider.user) {
        const author = await api.get(`/api/authors/${authProvider.user.uuid}/`);
        setCurrentAuthor(author.data);
      }
    };

    fetchPost();
    fetchAuthor();
  }, [postID, authProvider.user ? authProvider.user.uuid : null, navigate]);

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

    if (post) {
      fetchImage();
    }
  }, [post]);

  useEffect(() => {
    const fetchPost = async () => {
      if (postGiven) {
        const postData = await postService.getPost(`api/posts/${postGiven.id}`);
        setCommentList(postData.comments.src.reverse());
        setCommentCount(
          Array.isArray(postData.comments) ? 0 : postData.comments.count
        );
      }
    }
    fetchPost()
  }, [isModalOpen])

  const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src; // Return the fetched Base64 string if available, otherwise the original src
  };

  const handleToggleComment = () => {
    setIsCommentOpen(!isCommentOpen);
  };

  const handleCommentButtonClick = () => {
    if (isModal) return;
    setIsModalOpen(true);
  };

  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsModalOpen(false);
  };

  const handleNewComment = (newComment) => {
    const newCommentList = [newComment, ...commentList];
    const newCount = commentCount + 1;
    setCommentCount(newCount);
    setCommentList(newCommentList);
  };

  const handleSharePost = async () => {
    if (!post) return;
    setIsShareDialogOpen(true);
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

  return showAlert && canToggleComments ? (
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
            post.author.profileImage && post.author.profileImage.trim() !== "" ? // the nullish coalescing operator (??) treats empty as valid
            post.author.profileImage :
            `https://ui-avatars.com/api/?background=random&name=${post.author.displayName}`
          }
          alt={`${post.author.displayName}'s profile`}
          onClick={redirectToAuthorProfile}
        />
        <div className={styles.headerText}>
          <span className={styles.userName} onClick={redirectToAuthorProfile}>
            {post.author.displayName}
          </span>
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
              onClick={
                canToggleComments
                  ? handleToggleComment
                  : handleCommentButtonClick
              }
            >
              <i className="fas fa-comment"></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
          {post.visibility === 1 ? (
            <div
              className={styles.icon}
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
                src={
                  post.content.includes("data:image/" || "base64,")
                    ? post.content
                    : "data:image/png;base64," + post.content
                }
                alt={post.description}
              />
            </div>
          ) : (
            <div className={styles.postText}>
              {post.contentType === ContentType.MARKDOWN ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ node, children }) => {
                      // Check if the first child is an element with tagName "img"
                      const firstChild = node.children[0];
                      const isImage =
                        firstChild &&
                        "tagName" in firstChild &&
                        firstChild.tagName === "img";

                      // Only wrap in <p> if it is not an <img> tag
                      return isImage ? <>{children}</> : <p>{children}</p>;
                    },
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

      {(isCommentOpen && canToggleComments) || isModal ? (
        <div className={styles.comments}>
          <div className={styles.commentsHeader}>Comments</div>
          {currentAuthor && (
            <CommentInputField
              authorObj={currentAuthor}
              post={post}
              onCommentAdded={handleNewComment}
            />
          )}
          {commentList.map((comment) => (
            <div key={comment.id} className={styles.comment}>
              <div key={comment.id} className={styles.comment}>
                <Avatar
                  src={comment.author?.profileImage}
                  alt={comment.author?.displayName}
                  sx={{ marginRight: "0.5rem" }}
                >
                  {comment.author?.displayName.charAt(0)}
                </Avatar>
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

      <Modal open={isModalOpen} onClose={handleCommentModalClose}>
        <>
          <Post postGiven={post} canToggleComments={false} isModal={true} />
        </>
      </Modal>
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
