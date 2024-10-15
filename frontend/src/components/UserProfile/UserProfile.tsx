import MiniPostCard from "../MiniPostCard/MiniPostCard";
import styles from "./UserProfile.module.scss";

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
            <span>
              <p className={styles.count}>100</p> <p>posts</p>
            </span>
            <span>
              <p className={styles.count}>100</p> <p>followers</p>
            </span>
            <span>
              <p className={styles.count}>100</p> <p>following</p>
            </span>
          </section>
        </section>

        <section className={styles.userProfileLink}>
          <button className={styles.followButton}>Get Profile Link</button>
        </section>
      </section>
      <section className={styles.bioContainer}>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        </p>
      </section>
      <hr className={styles.horizontalLine} />
      <section className={styles.userPosts}>
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
          <MiniPostCard />
      </section>
    </div>
  );
}
