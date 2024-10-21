import FollowList from "../FollowList/FollowList";
import GitHubIcon from "@mui/icons-material/GitHub";
import { IconButton } from "@mui/material";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import axios from "axios";
import { checkAuth } from "../../util/auth/checkauth";
import styles from "./UserProfile.module.scss";
import { useEffect } from "react";
import { useState } from "react";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import EditPostModal from "../EditPostModal/EditPostModal";

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
  const [isEditPostModalOpen, setIsEditPostModalOpen] = useState(false);
  const [postToEdit, setPostToEdit] = useState<AuthorPost[] | null>(null);

  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await checkAuth();
        setUser({
          username: data.username,
          uuid: data.uuid,
        });
      } catch (error) {
        console.error("Error checking auth", error);
      }
    };

    fetchUser();
  }, []);

  const fetchAuthorPosts = async () => {
    try {
      const response = await axios.get<AuthorPost[]>(
        `http://localhost:8000/api/authors/${user.uuid}/posts/`
      );
      console.log(response.data);
      setAuthorPosts(response.data);
    } catch (error) {
      console.error("Error fetching the author posts", error);
    }
  };

  // fetch the author data from the API when the component mounts
  useEffect(() => {
    if (!user) return;

    const fetchAuthorData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/authors/${user.uuid}/`
        );
        console.log(response.data);
        setAuthorData(response.data);
      } catch (error) {
        console.error("Error fetching the author data", error);
      }
    };
    fetchAuthorData();
    fetchAuthorPosts();
  }, [user]);

  const handleDeletePostButtonClicked = (postId: string) => {
    setPostToDelete(postId);
    setIsPostDeleteModalOpen(true);
  };
  const handleDeletePostModalClose = () => {
    setIsPostDeleteModalOpen(false);
    setPostToDelete(null);
  };

  const csrfToken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  const handleConfirmDelete = async () => {
    if (postToDelete) {
      try {
        // API call to delete the post
        await axios.delete(
          `http://127.0.0.1:8000/api/authors/${user.uuid}/posts/${postToDelete}/`,
          {
            headers: {
              "x-csrftoken": csrfToken,
            },
          }
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

  const handleEditPostButtonClicked = async (postId: string) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/authors/${user.uuid}/posts/${postId}/`
      );
      setPostToEdit(response.data as AuthorPost[]); // Set the post data to edit
      setIsEditPostModalOpen(true); // Open the edit modal
    } catch (error) {
      console.error("Error fetching post data for editing", error);
    }
  };

  const handleEditPostModalClose = () => {
    setPostToEdit(null);
    setIsEditPostModalOpen(false);
  };

  const handleConfirmEdit = async (updatedPost: {
    title: string;
    content: string;
  }) => {
    if (postToEdit) {
      try {
        await axios.put(
          `http://127.0.0.1:8000/api/authors/${user.uuid}/posts/${postToEdit["id"]}/`,
          {
            title: updatedPost.title,
            content: updatedPost.content,
            type: "post", // Ensure the type is set correctly as per your PUT request
            // get the new modified post date
            published: new Date().toISOString(),
          }
        );

        // Refresh the posts after successful update
        await fetchAuthorPosts();

        // Close the modal after updating
        handleEditPostModalClose();
      } catch (error) {
        console.error("Error updating post", error);
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
            author={post.author.displayName}
            title={post.title}
            time={post.published}
            content={post.content}
            likes={1523382}
            saves={250}
            comments={10000}
            canDelete={true}
            handleDelete={() => handleDeletePostButtonClicked(post.id)}
            canEdit={true}
            handleEdit={() => handleEditPostButtonClicked(post.id)}
          />
        ))}
      </section>
      <DeletePostModal
        isOpen={isPostDeleteModalOpen}
        onRequestClose={handleDeletePostModalClose}
        onDelete={handleConfirmDelete}
      />
      <EditPostModal
        isOpen={isEditPostModalOpen}
        onRequestClose={handleEditPostModalClose}
        post={
          postToEdit
            ? { title: postToEdit[0].title, content: postToEdit[0].content }
            : { title: "", content: "" }
        }
        onSubmit={handleConfirmEdit} // Pass handleConfirmEdit here
      />
    </div>
  );
}
