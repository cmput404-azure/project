import { formatCount } from "../../util/formatting/formatCount";
import styles from "./MiniPostCard.module.scss";
import "@fortawesome/fontawesome-free/css/all.min.css";

interface MiniPostCardProps {
  profilePic?: string;
  author: string;
  time: string;
  title: String;
  content: string;
  image?: string;
  likes: number;
  saves: number;
  comments: number;
  canDelete?: boolean;
  handleDelete?: () => void;
}

function MiniPostCard({
  profilePic,
  author,
  time,
  title,
  content,
  image,
  likes,
  saves,
  comments,
  canDelete,
  handleDelete,
}: MiniPostCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.profileSection}>
          <img
            className={styles.profilePic}
            src={
              profilePic ??
              `https://ui-avatars.com/api/?background=random&name=${author}`
            }
            alt={author}
          />
          <div className={styles.userInfo}>
            <span className={styles.userName}>{author}</span>
            <span className={styles.postTime}>{time}</span>
          </div>
        </div>
        {canDelete ? (
          <i className="fas fa-trash-alt" onClick={handleDelete}></i>
        ) : null}
      </div>

      {image ? (
        <div className={styles.cardImage}>
          <img
            className={styles.postImage}
            src={image}
            alt="Mini post content"
          />
        </div>
      ) : (
        <div className={styles.imgPlaceholder}></div>
      )}

      <div className={styles.cardSummary}>{title}</div>

      <div className={styles.cardSummary}>{content}</div>

      <div className={styles.cardFooter}>
        <div className={styles.essentials}>
          <div className={styles.icon}>
            <i className="fas fa-heart"></i>
            <span>{formatCount(likes)}</span>
          </div>
          <div className={styles.icon}>
            <i className="fas fa-bookmark"></i>
            <span>{formatCount(saves)}</span>
          </div>
          <div className={styles.icon}>
            <i className="fas fa-comment"></i>
            <span>{formatCount(comments)}</span>
          </div>
        </div>
        <div className={styles.icon}>
          <i className="fas fa-share"></i>
        </div>
      </div>
    </div>
  );
}

export default MiniPostCard;