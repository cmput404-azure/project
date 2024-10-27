import { Author, Post } from "../../models/models";
import { useEffect, useState } from "react";

import EditProfileModal from "../EditProfileModal/EditProfileModal";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import EditPostModal from "../EditPostModal/EditPostModal";
import FollowList from "../FollowList/FollowList";
import GitHubIcon from "@mui/icons-material/GitHub";
import { IconButton } from "@mui/material";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import { api } from "../../service/config";
import styles from "./UserProfile.module.scss";
import { useAuth } from "../../state";
import followService from "../../service/follow";

interface AuthorPostsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Post[];
}

export default function UserProfile() {
  // Author data
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<Post[]>([]);
  // Edit profile
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  // Delete post
  const [isPostDeleteModalOpen, setIsPostDeleteModalOpen] = useState(false);
  const [postToDelete, setPostToDelete] = useState<string | null>(null);
  const [visibilityNumber, setVisibilityNumber] = useState<number | null>(null);
  // Edit post
  const [isEditPostModalOpen, setIsEditPostModalOpen] = useState(false);
  const [postToEdit, setPostToEdit] = useState<Post[]>([]);
  // FollowerList
  const [isFollowerListModalOpen, setIsFollowerListModalOpen] = useState(false);
  const [showFollowerList, setShowFollowerList] = useState<string>("");
    
  const [friendsCount, setFriendsCount] = useState(0);
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);

  const handleEditProfileButtonClicked = () => {
    setIsEditingProfile(true);
  };

  const fetchFriendsCount = async () => {
    try {
      const data = await followService.getFriends(authProvider.user.uuid);
      setFriendsCount(data.length);
    } catch (error) {
      console.error('Fetch error (friends):', error);
    }
  };

  const fetchFollowersCount = async () => {
    try {
      const data = await followService.getFollowers(authProvider.user.uuid);
      setFollowersCount(data.length);
    } catch (error) {
      console.error('Fetch error (followers):', error);
    }
  };

  const fetchFollowingCount = async () => {
    try {
      const data = await followService.getFollowing(authProvider.user.uuid);
      setFollowingCount(data.length);
    } catch (error) {
      console.error('Fetch error (following):', error);
    }
  };

  const handleSaveEditProfileButtonClicked = (data) => {
    let tempAuthorData = authorData;
    tempAuthorData.displayName = data.displayName;
    tempAuthorData.github = data.githubLink;
    updateUserInfo(tempAuthorData);
    console.log(data);
    setIsEditingProfile(false);
  };

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

  function openFollowers() {
    setShowFollowerList("Follower");
    setIsFollowerListModalOpen(true);
  }

  function openFollowing() {
    setShowFollowerList("Following");
    setIsFollowerListModalOpen(true);
  }
  function openFriends() {
    setShowFollowerList("Friends");
    setIsFollowerListModalOpen(true);
  }

  // authentication
  const authProvider = useAuth();

  useEffect(() => {
    const fetchCounts = async () => {
      await Promise.all([fetchFriendsCount(), fetchFollowersCount(), fetchFollowingCount()]);
    };

    fetchCounts();
    if (authProvider.user) {
      fetchAuthorData();
      fetchAuthorPosts();
    }
  }, [authProvider.user]);

  // function to get the info of the user who is currently logged in
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

  // function to update an Authors data
  async function updateUserInfo(data) {
    try {
      if (authProvider.user) {
        const response = await api.put(
          `/api/authors/${authProvider.user.uuid}/`,
          data
        );
        console.log("User info updated successfully:", response.data);
        fetchAuthorData();
        fetchAuthorPosts();
      }
    } catch (error) {
      console.error("Error updating user info", error);
    }
  }

  // function to get all the authors posts, used to refresh after save
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

        // Second request: Get the followers
        const followersResponse = await api.get<{
          type: string;
          followers: Author[];
        }>(`/api/authors/${authProvider.user.uuid}/followers/`);
        const followers = followersResponse.data["followers"];
        console.log("Followers retrieved:", followers);

        // Third request: Get the friends
        const friendsResponse = await api.get<Author[]>(
          `/api/authors/${authProvider.user.uuid}/following/?action=friends`
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
          id: postId,
          title: updatedPost.title,
          content: updatedPost.content,
          visibility: updatedPost.visibility,
        };

        if (postToEdit[0].visibility === 1 || postToEdit[0].visibility === 3) {
          for (const follower of uniqueFollowers) {
            const inboxUrl = `/api/authors/${follower.id}/inbox/`;
            try {
              const inboxResponse = await api.put<{ message: string }>(
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
            "Error sending noti on updated posts to followers' inboxes."
          );
        }

        // Friends receive inbox on all type of post
        for (const friend of friends) {
          const inboxUrl = `/api/authors/${friend.id}/inbox/`;
          try {
            const inboxResponse = await api.put<{ message: string }>(
              inboxUrl,
              payload
            );
            console.log(inboxResponse.data);
          } catch (error) {
            console.error(
              `Error sending noti on updated posts to ${friend.id}:`,
              error
            );
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

        // Second request: Get the followers
        const followersResponse = await api.get<{
          type: string;
          followers: Author[];
        }>(`/api/authors/${authProvider.user.uuid}/followers/`);
        const followers = followersResponse.data["followers"];
        console.log("Followers retrieved:", followers);

        // Third request: Get the friends
        const friendsResponse = await api.get<Author[]>(
          `/api/authors/${authProvider.user.uuid}/following/?action=friends`
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
        const config2 = {
          headers: {},
          data: {
            id: `/api/authors/${authProvider.user.uuid}/posts/${postToDelete}`,
            type: "post",
          },
        };

        if (visibilityNumber === 1 || visibilityNumber === 3) {
          for (const follower of uniqueFollowers) {
            const inboxUrl = `/api/authors/${follower.id}/inbox/`;
            try {
              const inboxResponse = await api.delete<{ message: string }>(
                inboxUrl,
                config2
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
          const inboxUrl = `/api/authors/${friend.id}/inbox/`;
          try {
            const inboxResponse = await api.delete<{ message: string }>(
              inboxUrl,
              config2
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
              <button
                className={styles.followButton}
                onClick={handleEditProfileButtonClicked}
              >
                Edit Profile
              </button>
              <IconButton
                onClick={() => window.open(authorData.github, "_blank")}
              >
                <GitHubIcon />
              </IconButton>
            </section>
          </section>

          {/* {          <span className={styles.userHandle}>
            @{authorData.displayName.toLowerCase().replace(" ", "_")}
          </span>} */}

          <section className={styles.userStats}>
            <span>
              <p className={styles.count}>100</p> <p>posts</p>
            </span>
            <span onClick={openFollowers} style={{ cursor: "pointer" }}>
              <p className={styles.count}>{followersCount}</p> <p>followers</p>
            </span>
            <span onClick={openFollowing} style={{ cursor: "pointer" }}>
              <p className={styles.count}>{followingCount}</p> <p>following</p>
            </span>
            <span onClick={openFriends} style={{ cursor: "pointer" }}>
              <p className={styles.count}>{friendsCount}</p>
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
      <EditProfileModal
        isOpen={isEditingProfile}
        onSave={handleSaveEditProfileButtonClicked}
        onClose={() => setIsEditingProfile(false)}
        author={authorData}
      />

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
