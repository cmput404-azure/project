import styles from './ProfileCard.module.scss';

const ProfileCard = () => {
  return (
    <div className={styles.card}>
        <div className={styles.cardHeader}>
            <div className={styles.profilePic}>
                <img src="../images/yellowduck.png" alt="Profile" />
            </div>

            <div className={styles.infoSection}>
                <div className={styles.userName}>Mr. Ducky</div>
                <div className={styles.userHandle}>@mr_ducky</div>
            </div>

            <div className={styles.cardButton}>
                <button>+</button>
            </div>
        </div>

        <div className={styles.userBio}>
            The author personal bio goes here. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut. The author personal bio goes here. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut. The author personal bio goes here. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.
        </div>
    </div>
  );
};

export default ProfileCard