import { useEffect, useState } from "react";

import DeletePostModal from "../DeletePostModal/DeletePostModal";
import FollowList from "../FollowList/FollowList";
import GitHubIcon from "@mui/icons-material/GitHub";
import { IconButton } from "@mui/material";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import axios from "axios";
import styles from "./UserProfile.module.scss";
import { useAuth } from "../../state";
import { useNavigate } from "react-router";

import { Author } from "../../models/models";

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

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

export default function UserProfile() {
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<AuthorPost[]>([]);
  const [isPostDeleteModalOpen, setIsPostDeleteModalOpen] = useState(false);
  const [postToDelete, setPostToDelete] = useState<string | null>(null);
  const [visibilityNumber, setVisibilityNumber] = useState<number | null>(null);
  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState(true);

  const authProvider = useAuth();

  async function fetchAuthorPosts() {
    try {
      if (authProvider.user) {
        const response = await axios.get<AuthorPost[]>(
          `http://localhost:8000/api/authors/${authProvider.user.uuid}/posts/`
        );
        setAuthorPosts(response.data);
      }
    } catch (error) {
      console.error("Error fetching the author posts", error);
    }
  }

  async function fetchAuthorData() {
    try {
      if (authProvider.user) {
        const response = await axios.get(
          `http://localhost:8000/api/authors/${authProvider.user.uuid}/`
        );
        setAuthorData(response.data);
      }
    } catch (error) {
      console.error("Error fetching the author data", error);
    }
  }

  const handleDeletePostButtonClicked = (
    postId: string,
    visibilityNumber: number
  ) => {
    setPostToDelete(postId);
    setVisibilityNumber(visibilityNumber);
    setIsPostDeleteModalOpen(true);
  };

  function handleDeletePostModalClose() {
    setIsPostDeleteModalOpen(false);
    setPostToDelete(null);
    setVisibilityNumber(null);
  }

  async function handleConfirmDelete() {
    if (postToDelete && authProvider.user) {
      try {
        // API call to delete the post
        await axios.delete(
          `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/posts/${postToDelete}/`
        );

        // Second request: Get the followers
        const followersResponse = await axios.get<{
          type: string;
          followers: Author[];
        }>(
          `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/followers/`
        );
        const followers = followersResponse.data["followers"];
        console.log("Followers retrieved:", followers);

        // Third request: Get the friends
        const friendsResponse = await axios.get<Author[]>(
          `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/following/?action=friends`
        );
        const friends = friendsResponse.data;
        console.log("Friends retrieved:", friends);

        // Now friends and followers may be duplicated, we have to go through and remove
        // one from the follower list if it also exist in friend
        // Create a Set of friend IDs for quick lookup
        const friendIds = new Set(friends.map((friend) => friend.id));

        // Filter out followers that are also friends
        const uniqueFollowers = followers.filter(
          (follower) => !friendIds.has(follower.id)
        );
        console.log("Filtered followers (excluding friends):", uniqueFollowers);

        // send to followers if post is public or unlisted
        // always send to friends for all type of posts
        const payload = {
          id: `http://127.0.0.1:8000/api/authors/${authProvider.user.uuid}/posts/${postToDelete}`,
          type: "post",
        };

        if (visibilityNumber == 1 || visibilityNumber == 3) {
          for (const follower of uniqueFollowers) {
            const inboxUrl = `http://127.0.0.1:8000/api/authors/${follower.id}/inbox/`;
            try {
              const inboxResponse = await axios.post<{ message: string }>(
                inboxUrl,
                payload
              );
              console.log(inboxResponse.data);
            } catch (error) {
              console.error(
                `Error sending post to inbox of ${follower.id}:`,
                error
              );
            }
          }
          console.log(
            "Error sending noti on deleted posts to followers' inboxes."
          );
        }

        // Friends receive inbox on all type of post
        for (const friend of friends) {
          const inboxUrl = `http://127.0.0.1:8000/api/authors/${friend.id}/inbox/`;
          try {
            const inboxResponse = await axios.post<{ message: string }>(
              inboxUrl,
              payload
            );
            console.log(inboxResponse.data);
          } catch (error) {
            console.error(
              `Error sending noti on deleted posts to ${friend.id}:`,
              error
            );
          }
        }

        // Refresh the posts after successful deletion
        await fetchAuthorPosts();

        // Close the modal after deletion
        setIsPostDeleteModalOpen(false);
        setPostToDelete(null);
        setVisibilityNumber(null);
      } catch (error) {
        console.error("Error deleting post", error);
      }
    }
  }

  function openFollowers() {
    setShowFollowerList(true);
    setIsFollowerListModalOpen(true);
  }

  function openFollowing() {
    setShowFollowerList(false);
    setIsFollowerListModalOpen(true);
  }

  useEffect(() => {
    if (authProvider.user) {
      fetchAuthorData();
      fetchAuthorPosts();
    }
  }, [authProvider.user]);

  if (!authorData) {
    return <div>Loading...</div>;
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
        {authorPosts.map((post) => (
          <MiniPostCard
            key={post.id}
            author={post.author.displayName}
            title={post.title}
            time={post.published}
            content={post.content}
            likes={1523382}
            saves={250}
            comments={10000}
            canDelete={true}
            handleDelete={() =>
              handleDeletePostButtonClicked(post.id, post.visibility)
            }
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
