import "@fortawesome/fontawesome-free/css/all.min.css";

import {
  Alert,
  CircularProgress,
  Modal,
  Snackbar,
  Tooltip,
} from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";

import Avatar from "@mui/material/Avatar";
import CommentInputField from "../CommentInput/CommentInput";
import { ContentType } from "../../models/modelTypes";
import EllipseMenu from "../EllipseMenu/EllipseMenu";
import FollowService from "../../service/follow";
import LinkIcon from '@mui/icons-material/Link';
import { PostData } from "../../models/models";
import { PostData as PostModel } from "../../models/models";
import ProfileService from "../../service/profile";
import ReactMarkdown from "react-markdown";
import { api } from "../../service/config";
import { decodeBase64ToUrl } from "../../util/rendering/decodeBase64ToUrl";
import { extractUUID } from "../../util/formatting/extractUUID";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";
import postService from "../../service/post";
import profileService from "../../service/profile";
import remarkGfm from "remark-gfm";
import styles from "./Post.module.scss";
import { useAuth } from "../../state";
import likeService from "../../service/like";

interface PostProps {
  postGiven?: PostModel;
  canToggleComments?: boolean;
  isModal?: boolean;
  isUserProfile?: boolean;
  onDeletePost?: (postId: string) => void;
}

export default function Post({
  postGiven,
  canToggleComments = true,
  isModal = false,
  isUserProfile = false,
  onDeletePost,
}: PostProps) {
  const { postID: postIDFromParams } = useParams<{ postID: string }>();
  const postID = postGiven ? null : postIDFromParams;
  const authProvider = useAuth();
  const navigate = useNavigate();

  const [post, setPost] = useState<PostModel | null>(null);
  const [postData, setPostData] = useState<PostData>(postGiven);
  const [canCopyLink, setCanCopyLink] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [commentCount, setCommentCount] = useState(0);
  const [hasLiked, setHasLiked] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isCommentOpen, setIsCommentOpen] = useState(false);
  const [commentList, setCommentList] = useState<any[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const [imageSrc, setImageSrc] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentAuthor, setCurrentAuthor] = useState<any>();
  const [postAuthorID, setPostAuthorID] = useState("");
  const prevIsModalOpenRef = useRef<boolean>();

  useEffect(() => {
    const fetchPost = async () => {
      try {
        if (postID) { // when opening the post via link
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
                if (normalizeVisibility(postData.visibility) !== 1) {
                  if (
                    !is_following &&
                    normalizeVisibility(postData.visibility) === 2
                  ) {
                    setOpenSnackbar(true);
                    setShowAlert(true);
                    setTimeout(() => {
                      navigate("/home");
                    }, 2000);
                  }
                }
              }
            }

            if (postData.likes.count > 0) {
              setHasLiked(
                postData.likes.src.some((like) =>
                  like.id.includes(authProvider.user?.uuid)
                )
              );
            }
          }

          setPost(postData);

          if ( authProvider.user.is_staff || postData.visibility === "PUBLIC" || postData.visibility === "UNLISTED" || postData.author.id.includes(authProvider.user.uuid) ) {
            setCanCopyLink(true);
          }

          setCommentList(postData.comments.src);
          setLikeCount(
            Array.isArray(postData.likes) ? 0 : postData.likes?.count || 0
          );
          setCommentCount(
            Array.isArray(postData.comments) ? 0 : postData.comments?.count || 0
          );
        } else {
          setPost(postGiven);

          if ( authProvider.user.is_staff || postGiven.visibility === "PUBLIC" || postData.visibility === "UNLISTED" || postGiven.author.id.includes(authProvider.user.uuid) ) {
            setCanCopyLink(true);
          }

          const postAuthorID = extractUUID(postGiven.author.id);
          setPostAuthorID(postAuthorID);

          if (authProvider.user && postGiven.likes?.count > 0) {
            setHasLiked(
              postGiven.likes.src.some((like) =>
                like.author.id.includes(authProvider.user.uuid) // whitesmoke changed the like.id so need to compare with author.id instead
              )
            );
          }

          const comments = Array.isArray(postGiven.comments?.src)
            ? postGiven.comments.src
            : [];
          setCommentList(comments);

          setLikeCount(
            Array.isArray(postData.likes) ? 0 : postData.likes?.count || 0
          );
          setCommentCount(
            Array.isArray(postData.comments) ? 0 : (postData.comments?.count || 0)
          );
        }
      } catch (error) {
        if (error.response && error.response.status === 403) {
          navigate("/login");
        } else if (error.response && error.response.status === 404) {
          navigate("/"); // back to stream since they are not an admin
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
            setImageSrc(imageUrl);
          } else {
            // If it's not a data URL, fetch from the endpoint
            try {
              if (imageUrl.endsWith('/image') && !post.id.toLowerCase().includes('whitesmoke')) {
                const response = await api.get<string>(imageUrl);
                const imageBase64 = response.data;
                setImageSrc(imageBase64);
              } else {
                const response = await api.get<PostData>(imageUrl);
                const jsonResponse = response.data;
                const imageData = `data:${jsonResponse.contentType},${jsonResponse.content}`;
                setImageSrc(imageData);
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

  // To refresh comment and like count when comment modal is closed
  useEffect(() => {
    const fetchPostComments = async () => {
      if (postGiven) {
        const commentsData = await postService.getPostComments(postGiven.id);
        const comments = Array.isArray(commentsData.src) ? commentsData.src : [];
        setCommentList(comments);
        setCommentCount(commentsData.count || 0);
        postGiven.comments = commentsData;
      }
    };

    const fetchPostLikes = async () => {
      if (postGiven) {
        const likes = await likeService.getLikes(postGiven.author.id, extractUUID(postGiven.id))
        post.likes = likes;
        setLikeCount(likes.count);
        
        if (authProvider.user && postGiven.likes?.count > 0) {
          setHasLiked(
            postGiven.likes.src.some((like) =>
              like.author.id.includes(authProvider.user.uuid) // whitesmoke changed the like.id so need to compare with author.id instead
            )
          );
        }
      }
    }

    if (prevIsModalOpenRef.current && !isModalOpen) {
      // The modal was open before and is now closed, so fetch comments
      fetchPostComments();
      fetchPostLikes();
    }
    prevIsModalOpenRef.current = isModalOpen;

  }, [isModalOpen, isCommentOpen]);

  const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src; // Return the fetched Base64 string if available, otherwise the original src
  };

  const handleToggleComment = () => {
    setIsCommentOpen(!isCommentOpen);
  };

  const handleCommentButtonClick = async () => {
    if (isModal) return;
    console.log(`IN HANDLE COMMENT BUTTON: ${JSON.stringify(post, null, 2)}`)
    try {
      setPost(post);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error fetching post data:", error);
    };
  }

  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsModalOpen(false);
  };

  const handleNewComment = (newComment) => {
    const newCommentList = [newComment, ...commentList];
    setCommentCount((prevCount) => prevCount + 1);
    setCommentList(newCommentList);
  };

  const handleLikePost = async () => {
    if (!authProvider.user) {
      navigate("/login");
      return;
    }

    if (hasLiked) return;

    console.log(`IN HANDLE LIKE POST: ${JSON.stringify(post, null, 2)}`)

    try {
      const like_obj = {
        type: "like",
        object: post.id, // should be the post FQID
        authorId: post.author.id
      }; // build json in the backend

      console.log(`LIKE OBJ: ${JSON.stringify(like_obj, null, 2)}`);
      await inbox.sendPostToInbox(post.author.id, like_obj);

      // update current post's likes so it's consistent
      const likes = await likeService.getLikes(post.author.id, extractUUID(post.id));
      post.likes = likes;
      setLikeCount(likeCount + 1);
      setHasLiked(true);
    } catch (error) {
      console.error("Error liking post:", error);
    }
  };

  const handleCopyLink = () => {
    if (post) {
      const domain = window.location.host;
      const path = `/#/post/${encodeURIComponent(post.id)}`;

      const link = `${domain}${path}`;
      navigator.clipboard.writeText(link).then(
        () => setOpenSnackbar(true),
        (err) => console.error("Could not copy link: ", err)
      );
    }
  };

  const redirectToAuthorProfile = () => {
    const encodedId = encodeURIComponent(post.author.id);
    const authorURL = `/authors/${encodedId}`;
    navigate(authorURL);
  };

  const handleCloseSnackbar = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason !== "clickaway") setOpenSnackbar(false);
  };

  if (!post)
    return (
      <div className={"loading_component"}>
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
        <div className="avatar">
          <Avatar
            className={styles.profilePic}
            src={profileService.getProfilePicture(post.author)}
            alt={`${post.author.displayName}'s profile`}
            onClick={redirectToAuthorProfile}
            sx={{
              "&:hover": {
                cursor: "pointer",
                boxShadow: "0 0 2px 2px #55555559",
              },
            }}
          />
        </div>
        <div className={styles.headerContainer}>
          <div className={styles.headerText}>
            <span className={styles.userName} onClick={redirectToAuthorProfile}>
              {post.author.displayName}
            </span>
            <span className={styles.postTime}>
              {new Date(post.published).toLocaleString('en-US', { year: '2-digit', month: '2-digit', day: '2-digit', hour: 'numeric', minute: '2-digit' })}
            </span>
          </div>
          <div>
          {normalizeVisibility(post.visibility) === 4 ? (<span className={styles.deletedLabel}>Deleted</span>) 
            : normalizeVisibility(post.visibility) === 3 ? (<span className={styles.unlistedLabel}>Unlisted</span>) 
            : normalizeVisibility(post.visibility) === 2 ? (<span className={styles.friendsOnlyLabel}>Friends-Only</span>) 
            : (<span className={styles.publicLabel}>Public</span>)}
          </div>
        </div>

        {authProvider.user?.uuid === postAuthorID && isUserProfile ? (
          <EllipseMenu
            post={postGiven}
            authorUUID={postGiven.author.id}
            onDelete={onDeletePost}
          />
        ) : (
          <Tooltip title={canCopyLink ? "Copy Link" : "Link Unavailable"}>
            <LinkIcon className={canCopyLink ? "" : styles.disabled} onClick={canCopyLink ? handleCopyLink : null} sx={{transform: "rotate(135deg)"}} />
          </Tooltip>
        )}

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
                  }
              }
            >
              <i
                className={"fas fa-heart icon"}
              ></i>
              <span>{formatCount(likeCount)}</span>
            </div>
            <div
              className={`${styles.icon}`}
              onClick={canToggleComments
                    ? handleToggleComment
                    : handleCommentButtonClick
              }
            >
              <i
                className={"fas fa-comment"}
              ></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
        </div>
        <div className={styles.cardContent}>
          <div className={styles.postTitle}>{post.title}</div>
          {post.contentType !== ContentType.MARKDOWN &&
            post.contentType !== ContentType.PLAIN ? (
            <div className={styles.imgContainer}>
              <img
                className={styles.postImage}
                src={
                  post.content.includes("data:image/") ||
                    post.content.includes("base64,")
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
          <div className={styles.commentsHeader} />
          {currentAuthor && (
            <CommentInputField
              authorObj={currentAuthor}
              post={post}
              onCommentAdded={handleNewComment}
            />
          )}
          <div className={styles.comment__list}>
            {commentList.map((comment) => (
              <div key={comment.id} className={styles.comment}>
                <div key={comment.id} className={styles.comment}>
                  <div className="avatar">
                    <Avatar
                      src={profileService.getProfilePicture(comment.author)}
                      alt={comment.author?.displayName}
                    />
                  </div>
                </div>
                <div className={styles.commentContent}>
                  <div className={styles.authorTime}>
                    <div className={styles.commentAuthor}>
                      {comment.author.displayName}
                    </div>
                    <div className={styles.timePosted}>
                      {new Date(comment.published).toLocaleString()}
                    </div>
                  </div>
                  <div className={styles.commentText}>{comment.comment}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}


      <Modal
        className={styles.post__modal}
        open={isModalOpen}
        onClose={handleCommentModalClose}
        sx={{ overflow: "auto" }}
      >
        <>
          <Post postGiven={post} canToggleComments={false} isModal={true} />
        </>
      </Modal>
    </div>
  );
}
