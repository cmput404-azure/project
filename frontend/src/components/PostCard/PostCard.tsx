import styles from './PostCard.module.scss';
import { formatCount } from '../../util/formatting/formatCount';
import '@fortawesome/fontawesome-free/css/all.min.css';

function PostCard() {
    // Example values
    const likeCount = 1523382;
    const saveCount = 250;
    const commentCount = 10000;

  return (
    <div className={styles.card}>
        <div className={styles.grid}>
            <img className={styles.profilePic} src="../images/yellowduck.png" alt="Profile" />
            <div className={styles.headerText}>
                <span className={styles.userName}>Mr. Ducky</span>
                <span className={styles.postTime}>11:11 PM</span>
            </div>
            <i className="fas fa-ellipsis-h"></i>
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
            <div className={styles.cardContent}>
                <div className={styles.postText}>Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs and the team for supporting my career. My supervisor, @dawgster has been supportive throughout my career, thanks for all your help and advice.</div>
                <div className={styles.imgContainer}>
                    <img className={styles.postImage} src="../images/ducklings.jpg" alt="Ducklings" />
                </div>
            </div>
        </div>

    </div>
  )
}

export default PostCard