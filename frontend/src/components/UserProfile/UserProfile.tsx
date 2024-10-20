import { useState } from "react";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import styles from "./UserProfile.module.scss";
import FollowList from "../FollowList/FollowList";
import axios from "axios";
import { useEffect } from "react";

export default function UserProfile() {
  const [authorData, setAuthorData] = useState(null);
  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState(true);

  // fetch the author data from the API when the component mounts
  useEffect(() => {
    const fetchAuthorData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/authors/5f577ee2-0ccc-49a4-b3cc-47a8aeb265df/"
        );
        setAuthorData(response.data); // Set the response data to state
      } catch (error) {
        console.error("Error fetching the author data", error);
      }
    };

    fetchAuthorData();
  }, []);

  // fetch the authors posts from the API when the component mounts

  const openFollowers = () => {
    setShowFollowerList(true);
    setIsFollowerListModalOpen(true);
  };

  const openFollowing = () => {
    setShowFollowerList(false);
    setIsFollowerListModalOpen(true);
  };

  if (!authorData) {
    return <div>Loading...</div>; // Display a loading message until data is fetched
  }

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
              <span className={styles.userName}>{authorData.displayName}</span>
            </section>
            <section className={styles.buttonContainer}>
              <button className={styles.followButton}>Follow</button>
              <a
                href={authorData.github}
                className={styles.githubButton}
                target="_blank" // Opens the link in a new tab
                rel="noopener noreferrer"
              >
                <img src="../images/githubIcon.png" alt="GitHub" />
              </a>
            </section>
          </section>

          <span className={styles.userHandle}>
            @{authorData.displayName.toLowerCase().replace(" ", "_")}
          </span>

          <section className={styles.userStats}>
            <span>
              <p className={styles.count}>100</p> <p>posts</p>
            </span>
            <span onClick={openFollowers} style={{ cursor: "pointer" }}>
              <p className={styles.count}>100</p> <p>followers</p>
            </span>
            <FollowList
              isOpen={isFollowerListModalOpen}
              onClose={() => setIsFollowerListModalOpen(false)}
              isFollowerList={showFollowerList}
            />
            <span onClick={openFollowing} style={{ cursor: "pointer" }}>
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
          userName={authorData.displayName}
          postTime="11:11 PM"
          postContent="Excited to share my promotion to Software Developer III, massive thanks to @CorgiLabs!"
          postImage="../images/ducklings.jpg"
          likeCount={1523382}
          saveCount={250}
          commentCount={10000}
        />
        {/* Add more MiniPostCard components as needed */}
      </section>
    </div>
  );
}
