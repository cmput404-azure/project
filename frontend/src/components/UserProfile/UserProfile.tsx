import { useState } from "react";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import styles from "./UserProfile.module.scss";
import FollowList from "../FollowList/FollowList";
import axios from "axios";
import { useEffect } from "react";
import Modal from "react-modal";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import GitHubIcon from "@mui/icons-material/GitHub";
import { IconButton } from "@mui/material";

interface Post {
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

// Modal needs this to be set so it knows where to put the modal in the DOM
Modal.setAppElement("#root");

export default function UserProfile() {
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<Post[]>([]);
  const [isPostDeleteModalOpen, setIsPostDeleteModalOpen] = useState(false);
  const [postToDelete, setPostToDelete] = useState<string | null>(null);
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
  const fetchAuthorPosts = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/authors/5f577ee2-0ccc-49a4-b3cc-47a8aeb265df/posts/"
      );
      setAuthorPosts(response.data as Post[]); // Set the response data to state
    } catch (error) {
      console.error("Error fetching the author posts", error);
    }
  };
  useEffect(() => {
    fetchAuthorPosts();
  }, []);

  const handleDeletePostButtonClicked = (postId: string) => {
    setPostToDelete(postId);
    setIsPostDeleteModalOpen(true);
  };
  const handleDeletePostModalClose = () => {
    setIsPostDeleteModalOpen(false);
    setPostToDelete(null);
  };

  const handleConfirmDelete = async () => {
    if (postToDelete) {
      try {
        // API call to delete the post
        await axios.delete(
          `http://127.0.0.1:8000/api/authors/5f577ee2-0ccc-49a4-b3cc-47a8aeb265df/posts/${postToDelete}/`
        );

        // Refresh the posts after successful deletion
        await fetchAuthorPosts();

        // Close the modal after deletion
        setIsPostDeleteModalOpen(false);
        setPostToDelete(null);
      } catch (error) {
        console.error("Error deleting post", error);
      }
    }
  };

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

      <hr className={styles.horizontalLine} />

      <section className={styles.userPosts}>
        {/* map the author post response data to the mini profile card component */}
        {authorPosts.map((post) => (
          <MiniPostCard
            key={post.id}
            profilePic="../../images/yellowduck.png"
            author={post.author.displayName}
            title={post.title}
            time={post.published}
            content={post.content}
            likes={1523382}
            saves={250}
            comments={10000}
            canDelete={true}
            handleDelete={() => handleDeletePostButtonClicked(post.id)}
          />
        ))}
      </section>
      <DeletePostModal
        isOpen={isPostDeleteModalOpen}
        onRequestClose={handleDeletePostModalClose}
        onDelete={handleConfirmDelete}
      />
    </div>
  );
}
