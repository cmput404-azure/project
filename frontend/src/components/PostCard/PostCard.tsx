import styles from "./PostCard.module.scss";
import { formatCount } from "../../util/formatting/formatCount";
import "@fortawesome/fontawesome-free/css/all.min.css";

interface PostCardProps {
  profilePic: string;
  userName: string;
  postTime: string;
  postContent: string;
  postImage?: string; // optional
  likeCount: number;
  saveCount: number;
  commentCount: number;
  onCommentButtonClick: () => void;
}

function PostCard({
  profilePic,
  userName,
  postTime,
  postContent,
  postImage,
  likeCount,
  saveCount,
  commentCount,
  onCommentButtonClick,
}: PostCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.grid}>
        <img
          className={styles.profilePic}
          src={profilePic}
          alt={`${userName}'s profile`}
        />
        <div className={styles.headerText}>
          <span className={styles.userName}>{userName}</span>
          <span className={styles.postTime}>{postTime}</span>
        </div>
        <div className={styles.icon}>
          <i className="fas fa-ellipsis-h"></i>
        </div>
        <div className={styles.cardFooter}>
          <div className={styles.essentials}>
            <div className={styles.icon}>
              <i className="fas fa-heart"></i>
              <span>{formatCount(likeCount)}</span>
            </div>
            <div className={styles.icon}>
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
          <div className={styles.postText}>{postContent}</div>
          {postImage ? (
            <div className={styles.imgContainer}>
              <img
                className={styles.postImage}
                src={postImage}
                alt="Post content"
              />
            </div>
          ) : (
            <div
              className={styles.imgPlaceholder}
            ></div> /* Placeholder for layout consistency */
          )}
        </div>
      </div>
    </div>
  );
}

export default PostCard;
