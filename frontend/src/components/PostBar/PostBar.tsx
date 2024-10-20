import React, { useState } from "react";
import axios from "axios";
import styles from "./PostBar.module.scss";

const UNKNOWN_USER_ID = "http://nodebbbb/api/authors/unknown";
const UNKNOWN_USER_NAME = "Unknown User";

interface PostBarProps {
  userImage: string;
  showButtonBar?: boolean;
}
type IconType = "public" | "friends" | "link";

const PostBar: React.FC<PostBarProps> = ({ userImage, showButtonBar }) => {
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




  const handleCombinedClick = () => {
    handleInboxClick();
    handlePostClick();
  };
  const handleInboxClick = async () => {
    const newPost = {
      type: "post",
      title: "New Post Title", // For simplicity, using a constant title
      id: `${UNKNOWN_USER_ID}/posts/${Date.now()}`, // Creating a unique ID for the post
      description: "A brief description of the post", // Using a placeholder description
      contentType: "text/plain",
      content: title,
      author: {
        type: "author",
        id: UNKNOWN_USER_ID,
        host: "http://nodebbbb/api/",
        displayName: UNKNOWN_USER_NAME,
        page: `${UNKNOWN_USER_ID}`,
        github: "http://github.com/unknownuser",
        profileImage: userImage,
      },
      comments: {
        type: "comments",
        id: `${UNKNOWN_USER_ID}/posts/${Date.now()}/comments`,
        page: `${UNKNOWN_USER_ID}/posts/${Date.now()}/comments`,
        page_number: 1,
        size: 5,
        count: 0,
        src: [],
      },
      likes: {
        type: "likes",
        id: `${UNKNOWN_USER_ID}/posts/${Date.now()}/likes`,
        page: `${UNKNOWN_USER_ID}/posts/${Date.now()}/likes`,
        page_number: 1,
        size: 50,
        count: 0,
        src: [],
      },
      published: new Date().toISOString(),
      visibility: activeIcon.toUpperCase(),
    };
    try {
      // Send a POST request to the backend
      const response = await axios.post(
        "http://your-backend-url.com/posts",
        newPost
      );
      console.log("Post successfully created:", response.data);
    } catch (error) {
      console.error("Error creating post:", error);
    }
  };
  const handlePostClick = async () => {};
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
            <div className={styles["vertical-divider"]}></div>
            <div
              className={`${styles["icon-section"]} ${
                activeIcon === "friends" ? styles.active : ""
              }`}
              onClick={() => handleIconClick("friends")}
            >
              <i className={`${styles.icon} ${styles["friend-icon"]}`}></i>
            </div>
            <div className={styles["vertical-divider"]}></div>
            <div
              className={`${styles["icon-section"]} ${
                activeIcon === "link" ? styles.active : ""
              }`}
              onClick={() => handleIconClick("link")}
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

