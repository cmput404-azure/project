import FollowList from "../FollowList/FollowList";
import GitHubIcon from '@mui/icons-material/GitHub';
import { IconButton } from "@mui/material";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import axios from "axios";
import styles from "./UserProfile.module.scss";
import { useEffect } from "react";
import { useState } from "react";

interface AuthorPost {
  type: string;
  title: string;
  id: string;
  contentType: string;
  content: string;
  author: {
    type: string;
    id: string;
    host: string;
    displayName: string;
    github: string;
    page: string;
    profileImage: string;
  };
  comments: any[];
  likes: any[];
  published: string;
  visibility: number;
}

export default function UserProfile() {
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<AuthorPost[]>([]);
  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState(true);

  // fetch the author data from the API when the component mounts
  useEffect(() => {
    const fetchAuthorData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/authors/a351a7a2-232d-44b1-a604-b63739d55d2c/"
        );
        console.log(response.data); // Log the response data to the console
        setAuthorData(response.data); // Set the response data to state
      } catch (error) {
        console.error("Error fetching the author data", error);
      }
    };

    async function fetchAuthorPosts(){
      try {
        const response = await axios.get<AuthorPost[]>(
          "http://localhost:8000/api/authors/a351a7a2-232d-44b1-a604-b63739d55d2c/posts/"
        );
        console.log(response.data); 
        setAuthorPosts(response.data); 
      } catch (error) {
        console.error("Error fetching the author data", error);
      }
    }

    fetchAuthorData();
    fetchAuthorPosts();
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
          src={`https://ui-avatars.com/api/?background=random&name=${authorData.displayName}`}
          alt={authorData.profilePic}
        />
        <section className={styles.userInfoContainer}>
          <section className={styles.userInfo}>
            <section className={styles.userNameContainer}>
              <span className={styles.userName}>{authorData.displayName}</span>
            </section>
            <section className={styles.buttonContainer}>
              <button className={styles.followButton}>Follow</button>
              <IconButton
                onClick={() => window.open(authorData.github, "_blank")}
              >
                <GitHubIcon />
              </IconButton>
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
        {authorPosts.map((post) => (
          <MiniPostCard
            key={post.id}
            title={post.title}
            content={post.content}
            author={post.author.displayName}
            time={post.published}
            comments={11}
            likes={12}
            saves={2}
          />
        ))}
      </section>
    </div>
  );
}
