import "@fortawesome/fontawesome-free/css/all.min.css";
import { Link } from "react-router-dom";

import { formatCount } from "../../util/formatting/formatCount";
import styles from "./PostCard.module.scss";

interface PostCardProps {
  profilePic: string;
  userName: string;
  postTime: string;
  postContent: string;
  likeCount: number;
  saveCount: number;
  commentCount: number;
  userID: string;
  onCommentButtonClick?: () => void; // optional
  onClick?: () => void;
}

function PostCard({
  profilePic,
  userName,
  postTime,
  postContent,
  likeCount,
  saveCount,
  commentCount,
  onCommentButtonClick,
  onClick,
  userID,
}: PostCardProps) {
  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.grid}>
        <Link to={`/authors/${userID}`}>
          <img
            className={styles.profilePic}
            src={
              profilePic ??
              `https://ui-avatars.com/api/?background=random&name=${userName}`
            }
            alt={`${userName}'s profile`}
          />
        </Link>
        <div className={styles.headerText}>
          <Link className={styles.userName} to={`/authors/${userID}`}>
            {userName}
          </Link>
          <span className={styles.postTime}>{postTime}</span>
        </div>
        <div className={styles.icon}>
          <i className="fas fa-ellipsis-h"></i>
        </div>
        <div className={styles.cardFooter}>
          <div className={styles.essentials}>
            <div
              className={styles.icon}
              onClick={(e) => {
                e.stopPropagation();
                console.log("Like");
              }}
            >
              <i className="fas fa-heart"></i>
              <span>{formatCount(likeCount)}</span>
            </div>
            <div
              className={styles.icon}
              onClick={(e) => {
                e.stopPropagation();
                console.log("Save");
              }}
            >
              <i className="fas fa-bookmark"></i>
              <span>{formatCount(saveCount)}</span>
            </div>
            <div className={styles.icon} onClick={onCommentButtonClick}>
              <i className="fas fa-comment"></i>
              <span>{formatCount(commentCount)}</span>
            </div>
          </div>
          <div className={styles.icon}>
            <i className="fas fa-share"></i>
          </div>
        </div>
        <div className={styles.cardContent}>
          {postContent.startsWith("data:") ? (
            <div className={styles.imgContainer}>
              <img
                src={postContent} // data url as the src to render the image
                alt="Post Content"
              />
            </div>
          ) : (
            <div className={styles.postText}>{postContent}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PostCard;
