import { Author, Post } from "../../models/models";
import { useEffect, useState } from "react";

import follow from "../../service/follow";
import inbox from "../../service/inbox";

import DeletePostModal from "../DeletePostModal/DeletePostModal";
import EditPostModal from "../EditPostModal/EditPostModal";
import FollowList from "../FollowList/FollowList";
import GitHubIcon from "@mui/icons-material/GitHub";
import { IconButton } from "@mui/material";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import { api } from "../../service/config";
import styles from "./UserProfile.module.scss";
import { useAuth } from "../../state";

interface AuthorPostsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Post[];
}

export default function UserProfile() {
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<Post[]>([]);
  const [isPostDeleteModalOpen, setIsPostDeleteModalOpen] = useState(false);
  const [postToDelete, setPostToDelete] = useState<string | null>(null);
  const [visibilityNumber, setVisibilityNumber] = useState<number | null>(null);

  const [isEditPostModalOpen, setIsEditPostModalOpen] = useState(false);
  const [postToEdit, setPostToEdit] = useState<Post[]>([]);
  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState<string>("");

  const authProvider = useAuth();

  async function fetchAuthorPosts() {
    try {
      if (authProvider.user) {
        const response = await api.get<AuthorPostsResponse>(
          `/api/authors/${authProvider.user.uuid}/posts/`
        );
        setAuthorPosts(response.data.results.reverse());
      }
    } catch (error) {
      console.error("Error fetching the author posts", error);
    }
  }

  async function fetchAuthorData() {
    try {
      if (authProvider.user) {
        const response = await api.get(
          `/api/authors/${authProvider.user.uuid}/`
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

  const handleEditPostButtonClicked = (postId: string) => {
    setPostToEdit(authorPosts.filter((post) => post.id === postId));
    setIsEditPostModalOpen(true);
  };

  function handleDeletePostModalClose() {
    setIsPostDeleteModalOpen(false);
    setPostToDelete(null);
    setVisibilityNumber(null);
  }

  function handleEditPostModalClose() {
    setIsEditPostModalOpen(false);
    setPostToEdit([]);
  }

  // Function to handle updating the post
  async function handleUpdatePost(updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) {
    if (postToEdit.length > 0 && authProvider.user) {
      try {
        const postId = postToEdit[0].id;

        // PUT request to update the post
        const response = await api.put(
          `/api/authors/${authProvider.user.uuid}/posts/${postId}/`,
          {
            title: updatedPost.title,
            content: updatedPost.content,
            visibility: updatedPost.visibility,
          }
        );

        // Get friends and followers list
        const followers = await follow.getFollowers(authProvider.user.uuid);
        const friends =  await follow.getFriends(authProvider.user.uuid);

        // followers already include all followers and friends
        // public/unlisted=> send to followers and friends
        if (postToEdit[0].visibility === 1 || postToEdit[0].visibility === 3) {
          for (const follower of followers) {
            const inboxResponse = await inbox.updateInboxPost(follower.id, postId, 
                                                              updatedPost.title, 
                                                              updatedPost.content, 
                                                              updatedPost.visibility);
          }
        } else { 
          for (const friend of friends) {
            const inboxResponse = await inbox.updateInboxPost(friend.id, postId, 
                                                              updatedPost.title, 
                                                              updatedPost.content, 
                                                              updatedPost.visibility);
          }
        }



        console.log("Post updated successfully:", response.data);

        // call again to refresh teh posts
        await fetchAuthorPosts();
        // close modal after updating the post
        handleEditPostModalClose();
      } catch (error) {
        console.error("Error updating post", error);
      }
    }
  }

  async function handleConfirmDelete() {
    if (postToDelete && authProvider.user) {
      try {
        // API call to delete the post
        await api.delete(
          `/api/authors/${authProvider.user.uuid}/posts/${postToDelete}/`
        );

        // Get friends and followers list
        const followers = await follow.getFollowers(authProvider.user.uuid);
        const friends =  await follow.getFriends(authProvider.user.uuid);

        // followers already include friends and followers
        if (visibilityNumber === 1 || visibilityNumber === 3) {
          for (const follower of followers) {
            const inboxResponse = await inbox.deleteInboxPost(follower.id, postToDelete);
          }
        } else {
          // Friends receive inbox on all type of post
          for (const friend of friends) {
            const inboxResponse = await inbox.deleteInboxPost(friend.id, postToDelete);
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
    setShowFollowerList("follower");
    setIsFollowerListModalOpen(true);
  }

  function openFollowing() {
    setShowFollowerList("following");
    setIsFollowerListModalOpen(true);
  }
  function openFriends() {
    setShowFollowerList("friend");
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
            <span onClick={openFriends} style={{ cursor: "pointer" }}>
              <p className={styles.count}>10</p>
              <p>friends</p>
            </span>
            <FollowList
              isOpen={isFollowerListModalOpen}
              onClose={() => setIsFollowerListModalOpen(false)}
              isFollowerList={showFollowerList}
            ></FollowList>
          </section>
        </section>

        <section className={styles.userProfileLink}>
          <button className={styles.followButton}>Get Profile Link</button>
        </section>
      </section>

      <hr className={styles.horizontalLine} />

      <section className={styles.userPostContainer}>
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
              canEdit={true}
              handleEdit={() => handleEditPostButtonClicked(post.id)}
            />
          ))}
        </section>
      </section>
      <DeletePostModal
        isOpen={isPostDeleteModalOpen}
        onRequestClose={handleDeletePostModalClose}
        onDelete={handleConfirmDelete}
      />

      <EditPostModal
        isOpen={isEditPostModalOpen}
        onRequestClose={handleEditPostModalClose}
        post={postToEdit.length > 0 ? postToEdit[0] : null}
        onSubmit={handleUpdatePost}
      />
    </div>
  );
}
