import { formatCount } from '../../util/formatting/formatCount';
import styles from './MiniPostCard.module.scss';
import '@fortawesome/fontawesome-free/css/all.min.css';

interface MiniPostCardProps {
    profilePic: string;
    userName: string;
    postTime: string;
    postContent: string;
    postImage?: string;
    likeCount: number;
    saveCount: number;
    commentCount: number;
}

function MiniPostCard({
    profilePic,
    userName,
    postTime,
    postContent,
    postImage,
    likeCount,
    saveCount,
    commentCount
}: MiniPostCardProps) {

  return (
    <div className={styles.card}>
        <div className={styles.cardHeader}>
            <div className={styles.profileSection}>
            <img className={styles.profilePic} src={profilePic} alt={`${userName}'s profile`} />
            <div className={styles.userInfo}>
                <span className={styles.userName}>{userName}</span>
                <span className={styles.postTime}>{postTime}</span>
            </div>
            </div>
            <i className="fas fa-ellipsis-h"></i>
        </div>

        { postImage ? (
            <div className={styles.cardImage}>
                <img className={styles.postImage} src={postImage} alt="Mini post content" />
            </div>
        ) : (
            <div className={styles.imgPlaceholder}></div>
        )}
        
        <div className={styles.cardSummary}>
            {postContent}
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
            <div className={styles.icon}>
                <i className="fas fa-comment"></i>
                <span>{formatCount(commentCount)}</span>
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
