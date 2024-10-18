import { useState } from "react";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import styles from "./UserProfile.module.scss";
import FollowList from "../FollowList/FollowList";

export default function UserProfile() {

  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState(true);

  const openFollowers = () => {
    setShowFollowerList(true);
    setIsFollowerListModalOpen(true);
  };

  const openFollowing = () => {
    setShowFollowerList(false);
    setIsFollowerListModalOpen(true);
  };
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
            <span onClick={openFollowers} style={{ cursor: 'pointer' }}>
              <p className={styles.count}>100</p> <p>followers</p>
            </span>
            <FollowList
              isOpen={isFollowerListModalOpen}
              onClose={() => setIsFollowerListModalOpen(false)}
              isFollowerList={showFollowerList}
            />
            <span onClick={openFollowing} style={{ cursor: 'pointer' }}>
              <p className={styles.count}>100</p> <p>following</p>
            </span>
            <FollowList
              isOpen={isFollowerListModalOpen}
              onClose={() => setIsFollowerListModalOpen(false)}
              isFollowerList={showFollowerList}
            />
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
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
        <MiniPostCard
          profilePic="../images/yellowduck.png"
          userName="Mr. Ducky"
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000} />
      </section>
    </div>
  );
}
