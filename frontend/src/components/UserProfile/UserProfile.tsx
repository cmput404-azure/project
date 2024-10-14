import styles from "./UserProfile.module.scss";
import GitHubIcon from "@mui/icons-material/GitHub";

export default function UserProfile() {
  return (
    <div className={styles.userProfileContainer}>
      <section className={styles.profileHeaderContainer}>
        <img
          className={styles.profilePic}
          src="../images/yellowduck.png"
          alt="Profile"
        />
        <section className={styles.userInfoContainer}>
          <section className={styles.userInfo}>
            <section className={styles.userNameContainer}>
              <span className={styles.userName}>Mr. Ducky</span>
            </section>
            <section className={styles.buttonContainer}>
              <button className={styles.followButton}>Follow</button>
              <a href="https://github.com" className={styles.githubButton}>
                <img src="../images/githubIcon.png" />
              </a>
            </section>
          </section>

          <span className={styles.userHandle}>@mr_ducky</span>

          <section className={styles.userStats}>
            <span>Posts: 100</span>
            <span>Followers: 100</span>
            <span>Following: 100</span>
          </section>
        </section>
      </section>
      <section className={styles.bioContainer}>
        <p>this is the bio</p>
      </section>
      <hr className={styles.horizontalLine} />
      <section className={styles.userPosts}>
        <p>Posts</p>
      </section>
    </div>
  );
}
