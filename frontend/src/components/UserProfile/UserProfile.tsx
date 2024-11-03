import { Author, PostData as Post } from "../../models/models";
import { CircularProgress, IconButton } from "@mui/material";
import { useEffect, useState } from "react";

import { AuthorPostsResponse } from "../../models/models";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import EditPostModal from "../EditPostModal/EditPostModal";
import EditProfileModal from "../EditProfileModal/EditProfileModal";
import FollowList from "../FollowList/FollowList";
import GitHubIcon from "@mui/icons-material/GitHub";
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import follow from "../../service/follow";
import followService from "../../service/follow";
import inbox from "../../service/inbox";
import styles from "./UserProfile.module.scss";
import { useAuth } from "../../state";
import { useParams } from "react-router-dom";

// by default isViewing is false which means the user is viewing their own profile
export default function UserProfile() {
  // Author data
  const [authorData, setAuthorData] = useState(null);
  const [authorPosts, setAuthorPosts] = useState<Post[]>([]);
  // Get the userID from the URL, used for viewing other users profile
  const { userID } = useParams<{ userID: string }>();
  const [userToGet, setUserToGet] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
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
  // Profile Link
  const [hasCopiedProfileLink, setHasCopiedProfileLink] = useState(false);

  const handleEditProfileButtonClicked = () => {
    setIsEditingProfile(true);
  };

  const fetchFriendsCount = async () => {
    try {
      const data = await followService.getFriends(authProvider.user.uuid);
      setFriendsCount(data.length);
    } catch (error) {
      console.error("Fetch error (friends):", error);
    }
  };

  const fetchFollowersCount = async () => {
    try {
      const data = await followService.getFollowers(authProvider.user.uuid);
      setFollowersCount(data.length);
    } catch (error) {
      console.error("Fetch error (followers):", error);
    }
  };

  const fetchFollowingCount = async () => {
    try {
      const data = await followService.getFollowing(authProvider.user.uuid);
      setFollowingCount(data.length);
    } catch (error) {
      console.error("Fetch error (following):", error);
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
    setPostToDelete(extractUUID(postId));
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

  // From https://devsarticles.com/react-copy-to-clipboard, Downloaded on 2024-10-26
  async function handleGetProfileLinkButtonClicked() {
    console.log("Get Profile Link button clicked");
    console.log(window.location.href);

    // From https://stackoverflow.com/questions/39823681/read-the-current-full-url-with-react, Downloaded on 2024-10-27
    let url = window.location.href;
    let parse = url.split("/");
    let hostDomain = parse.slice(0, 3).join("/") + "/";

    const content = `${hostDomain}#/authors/${extractUUID(authorData.id)}`;

    try {
      await navigator.clipboard.writeText(content);
      console.log("Copied to clipboard:", content);
      setHasCopiedProfileLink(true);
    } catch (error) {
      console.error("Unable to copy to clipboard:", error);
    }
  }

  function handleFollowButtonClicked() {
    console.log("Follow button clicked");
    // TODO: Implement follow functionality
    // addFollower();
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
      try {
        await Promise.all([
          fetchFriendsCount(),
          fetchFollowersCount(),
          fetchFollowingCount(),
        ]);
      } catch (error) {
        console.error("Failed to fetch counts:", error);
      }
    };

    if (userID) {
      console.log(userID);
      setUserToGet(userID);
      setIsEditing(false);
    } else if (authProvider.user) {
      fetchCounts();
      setHasCopiedProfileLink(false);

      setUserToGet(authProvider.user.uuid);
      setIsEditing(true);
    }
  }, [userID, authProvider.user]);

  useEffect(() => {
    // Only fetch data if userToGet is defined
    if (userToGet) {
      fetchAuthorData();
      fetchAuthorPosts();
    }
  }, [userToGet]);

  // function to get the info of the user who is currently logged in
  async function fetchAuthorData() {
    try {
      if (userToGet) {
        const response = await api.get(`/api/authors/${userToGet}/`);
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
          `/api/authors/${userToGet}/posts/`
        );
        // filter out the posts that are not publicaly visible
        const posts = response.data.src.filter((post) => post.visibility == 1);
        setAuthorPosts(posts.reverse());
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
        const postId = extractUUID(postToEdit[0].id);

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
        const friends = await follow.getFriends(authProvider.user.uuid);

        // followers already include all followers and friends
        // public/unlisted=> send to followers and friends
        if (postToEdit[0].visibility === 1 || postToEdit[0].visibility === 3) {
          for (const follower of followers) {
            const inboxResponse = await inbox.updateInboxPost(
              follower.id,
              postId,
              updatedPost.title,
              updatedPost.content,
              updatedPost.visibility
            );
          }
        } else {
          for (const friend of friends) {
            const inboxResponse = await inbox.updateInboxPost(
              friend.id,
              postId,
              updatedPost.title,
              updatedPost.content,
              updatedPost.visibility
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

        // Get friends and followers list
        const followers = await follow.getFollowers(authProvider.user.uuid);
        const friends = await follow.getFriends(authProvider.user.uuid);

        // followers already include friends and followers
        if (visibilityNumber === 1 || visibilityNumber === 3) {
          for (const follower of followers) {
            const inboxResponse = await inbox.deleteInboxPost(
              follower.id,
              postToDelete
            );
          }
        } else {
          // Friends receive inbox on all type of post
          for (const friend of friends) {
            const inboxResponse = await inbox.deleteInboxPost(
              friend.id,
              postToDelete
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

  // not used yet
  // const addFollower = async () => {
  //   const encodedHost = encodeURIComponent(authorData.host);
  //   const encodedId = encodeURIComponent(authorData.id);

  //   const encodedUrl = `${encodedHost}/api/authors/${encodedId}`;
  //   // Add actor as follower
  //   const response = await api.put(
  //     `/api/authors/${authProvider.user.uuid}/followers/${encodedUrl}/`
  //   );

  //   const data = response.data;
  // };

  if (!authorData) {
    return (
      <div className={"loading"}>
        <CircularProgress sx={{color: "#70ffaf"}}/>
      </div>
    );
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
              {isEditing ? (
                <button
                  className={styles.followButton}
                  onClick={handleEditProfileButtonClicked}
                >
                  Edit Profile
                </button>
              ) : (
                <button
                  className={styles.followButton}
                  onClick={handleFollowButtonClicked}
                >
                  Follow
                </button>
              )}

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
          <button
            className={
              hasCopiedProfileLink ? styles.linkCopied : styles.followButton
            }
            onClick={handleGetProfileLinkButtonClicked}
          >
            {hasCopiedProfileLink ? "Link Copied" : "Get Profile Link"}
          </button>
        </section>
      </section>

      <hr className={styles.horizontalLine} />

      <section className={styles.userPostContainer}>
        <div className={styles.userPosts}>
          {authorPosts.map((post) => (
            <MiniPostCard
              key={post.id}
              authorUUID={authorData.id}
              post={post}
            />
          ))}
        </div>
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
