import React, { useState } from "react";
import axios from "axios";
import styles from "./PostBar.module.scss";
import { getVisibilityNumber, VisibilityChoices } from "../../models/modelTypes";
import {Author, Post, Inbox} from "../../models/models"

const USER_ID = "8954d4e1-cefe-449c-b623-a9a51ba83d2f"; // this is test user

interface PostBarProps {
  userImage: string;
  showButtonBar?: boolean;
}
type IconType = "public" | "friends" | "unlisted";

const PostBar: React.FC<PostBarProps> = ({
  userImage,
  showButtonBar = true,
}) => {
  const [activeIcon, setActiveIcon] = useState<IconType>("public");
  const [title, setTitle] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");

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
  const handleInputClick = () => setShowDetail(true) ;
  const handleDescriptionChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => setDescription(event.target.value);
  const handleContentChange = (event: React.ChangeEvent<HTMLTextAreaElement>) =>
    setContent(event.target.value);

  const handleCombinedClick = async () => {
    try {
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
  
      const postResponse = await axios.post<Post>(
        `http://127.0.0.1:8000/api/authors/${USER_ID}/posts/`,
        newPost
      );
      console.log("Post successfully created:", postResponse.data);
  
      // Second request: Get the followers
      const followersResponse = await axios.get<{ type: string, followers: Author[] }>(
        `http://127.0.0.1:8000/api/authors/${USER_ID}/followers/`,
      );
      const followers = followersResponse.data["followers"];
      console.log("Followers retrieved:", followers);

      
      // Third request: Get the friends
      const friendsResponse = await axios.get<Author[]>(
        `http://127.0.0.1:8000/api/authors/${USER_ID}/following/?action=friends`,
      );
      const friends = friendsResponse.data;
      console.log("Friends retrieved:", friends);

      if (visibilityNumber == 1 || visibilityNumber == 3) {
        // If public or unlisted, send to friends and followers
        for (const follower of followers) {
          const inboxUrl = `http://127.0.0.1:8000/api/authors/${follower.id}/inbox/`;
          try {
            const inboxResponse = await axios.post<{message: string}>(inboxUrl, postResponse.data);
            console.log(inboxResponse.data);
          } catch (error) {
            console.error(`Error sending post to inbox of ${follower.id}:`, error);
          }
        }
        console.log("All posts sent to followers' inboxes.");
      }
      // Friends receive inbox on all type of post
      for (const friend of friends) {
        const inboxUrl = `http://127.0.0.1:8000/api/authors/${friend.id}/inbox/`;
        try {
          const inboxResponse = await axios.post<{message: string}>(inboxUrl, postResponse.data);
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
  
  return (
    <div className={styles.container}>
      <section className={styles["post-bar"]}>
        <img src={userImage} alt="User" className={styles["user-image"]} />
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


      {(showButtonBar || showDetail)  && (
        <section className={styles["button-bar"]}>
          <div className={styles["icon-bar"]}>
            <div
              className={`${styles["icon-section"]} ${
                activeIcon === "public" ? styles.active : ""
              }`}
              onClick={() => handleIconClick("public")}
            >
              <i className={`${styles.icon} ${styles["public-icon"]}`}></i>
            </div>
            <div
              className={`${styles["icon-section"]} ${
                activeIcon === "friends" ? styles.active : ""
              }`}
              onClick={() => handleIconClick("friends")}
            >
              <i className={`${styles.icon} ${styles["friend-icon"]}`}></i>
            </div>
            <div
              className={`${styles["icon-section"]} ${
                activeIcon === "unlisted" ? styles.active : ""
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

