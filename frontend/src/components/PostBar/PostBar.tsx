import { Author, Post } from "../../models/models";
import React, { useState } from "react";
import { VisibilityChoices, getVisibilityNumber } from "../../models/modelTypes";

import { api } from "../../service/config";
import styles from "./PostBar.module.scss";
import { useAuth } from "../../state";

interface PostBarProps {
  showButtonBar?: boolean;
}
type IconType = "public" | "friends" | "unlisted";

const PostBar: React.FC<PostBarProps> = ({
  showButtonBar = true,
}) => {
  const [activeIcon, setActiveIcon] = useState<IconType>("public");
  const [title, setTitle] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");

  const authProvider = useAuth();

  // To update the activeIcon
  const handleIconClick = (icon: IconType) => {
    setActiveIcon(icon);
  };
  // To update the title
  const handleTitleChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setTitle(event.target.value);
  };
  const handleInputClick = () => setShowDetail(true);
  const handleDescriptionChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => setDescription(event.target.value);
  const handleContentChange = (event: React.ChangeEvent<HTMLTextAreaElement>) =>
    setContent(event.target.value);

  const handleCombinedClick = async () => {
    try {
      console.log(authProvider.isAuthenticated)
      if (!authProvider.isAuthenticated) {
        console.error("User not loaded yet.");
        return;
      }

      // First request: Create a new post
      const visibilityNumber = getVisibilityNumber(activeIcon.toUpperCase() as VisibilityChoices);

      const newPost = {
        type: "post",
        title: title,
        description: description,
        contentType: "text/plain",
        content: content,
        published: new Date().toISOString(),
        visibility: visibilityNumber,
      };

      const postResponse = await api.post<Post>(
        `/api/authors/${authProvider.user.uuid}/posts/`,
        newPost
      );
      console.log("Post successfully created:", postResponse.data);

      // Second request: Get the followers
      const followersResponse = await api.get<{ type: string, followers: Author[] }>(
        `/api/authors/${authProvider.user.uuid}/followers/`
      );
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
      const friendIds = new Set(friends.map(friend => friend.id));

      // Filter out followers that are also friends
      const uniqueFollowers = followers.filter(follower => !friendIds.has(follower.id));
      console.log("Filtered followers (excluding friends):", uniqueFollowers);

      // send to followers if post is public or unlisted
      // always send to friends for all type of posts
      if (visibilityNumber === 1 || visibilityNumber === 3) {
        for (const follower of uniqueFollowers) {
          const inboxUrl = `/api/authors/${follower.id}/inbox/`;
          try {
            const inboxResponse = await api.post<{ message: string }>(inboxUrl, postResponse.data);
            console.log(inboxResponse.data);
          } catch (error) {
            console.error(`Error sending post to inbox of ${follower.id}:`, error);
          }
        }
        console.log("All posts sent to followers' inboxes.");
      }

      // Friends receive inbox on all type of post
      for (const friend of friends) {
        const inboxUrl = `/api/authors/${friend.id}/inbox/`;
        try {
          const inboxResponse = await api.post<{ message: string }>(inboxUrl, postResponse.data);
          console.log(inboxResponse.data);
        } catch (error) {
          console.error(`Error sending post to friend's inbox of ${friend.id}:`, error);
        }
      }
      console.log("All posts sent to followers/friends' inboxes.");

      // Closse the input modal and reset input fields
      setShowDetail(false)
      setTitle("")
      setDescription("")
      setContent("")

    } catch (error) {
      console.error("Error in combined request flow:", error);
    }
  };

  if (!authProvider.isAuthenticated) {
    return <></>
  }

  return (
    <div className={styles.container}>
      <section className={styles["post-bar"]}>
        <img src={authProvider.user.profileImage ?? `https://ui-avatars.com/api/?background=random&name=${authProvider.user.username}`} alt="User" className={styles["user-image"]} />
        <div className={styles["vertical-divider"]}></div>
        <input
          type="text"
          placeholder="Start your post with a title "
          className={styles["post-input"]}
          value={title}
          onChange={handleTitleChange}
          onClick={handleInputClick}
        />
        <button
          className={styles["add-button"]}
          onClick={() => console.log("Add button clicked")}
        >
          <span>+</span>
        </button>


      </section>

      {showDetail && (
        <div className={styles["detail-container"]}>
          <label className={styles["input-label"]}>Description</label>
          <textarea
            className={styles["description-input"]}
            placeholder="Add a brief description..."
            value={description}
            onChange={handleDescriptionChange}
          />

          <label className={styles["input-label"]}>Content</label>
          <textarea
            className={styles["content-input"]}
            placeholder="Write your post content here..."
            value={content}
            onChange={handleContentChange}
          />
        </div>
      )}


      {(showButtonBar || showDetail) && (
        <section className={styles["button-bar"]}>
          <div className={styles["icon-bar"]}>
            <div
              className={`${styles["icon-section"]} ${activeIcon === "public" ? styles.active : ""
                }`}
              onClick={() => handleIconClick("public")}
            >
              <i className={`${styles.icon} ${styles["public-icon"]}`}></i>
            </div>
            <div className={styles["vertical-divider"]}></div>
            <div
              className={`${styles["icon-section"]} ${activeIcon === "friends" ? styles.active : ""
                }`}
              onClick={() => handleIconClick("friends")}
            >
              <i className={`${styles.icon} ${styles["friend-icon"]}`}></i>
            </div>
            <div className={styles["vertical-divider"]}></div>
            <div
              className={`${styles["icon-section"]} ${activeIcon === "unlisted" ? styles.active : ""
                }`}
              onClick={() => handleIconClick("unlisted")}
            >
              <i className={`${styles.icon} ${styles["link-icon"]}`}></i>
            </div>
          </div>
          <button
            className={styles["post-button"]}
            onClick={handleCombinedClick}
          >
            Post
          </button>
        </section>
      )}
    </div>
  );
};

export default PostBar;

