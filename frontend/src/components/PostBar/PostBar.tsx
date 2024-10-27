import { Author, Post } from "../../models/models";
import React, { useState, useEffect, useRef } from "react";
import {
  VisibilityChoices,
  getVisibilityNumber,
} from "../../models/modelTypes";

import { api } from "../../service/config";
import styles from "./PostBar.module.scss";
import { useAuth } from "../../state";

interface PostBarProps {
  author?: any;
}
type IconType = "public" | "friends" | "unlisted";

// Max character limits
const TITLE_MAX_LENGTH = 200;

const PostBar: React.FC<PostBarProps> = ({ author }) => {
  const [activeIcon, setActiveIcon] = useState<IconType>("public");
  const [title, setTitle] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [activeCommonMark, setActiveCommonMark] = useState(false);
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [contentType, setContentType] = useState("");
  const authProvider = useAuth();

  const postBarRef = useRef<HTMLDivElement>(null); // Ref for the component
  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (postBarRef.current && !postBarRef.current.contains(event.target as Node)) {
        setShowDetail(false); // Hide details when clicking outside
      }
    };
  
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);
  

  // To update the activeIcon
  const handleIconClick = (icon: IconType) => {
    setActiveIcon(icon);
  };

  // To update the title
  const handleTitleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (event.target.value.length <= TITLE_MAX_LENGTH) {
      setTitle(event.target.value);
    }
  };

  const handleInputClick = () => setShowDetail(true);

  const handleDescriptionChange = (
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) => setDescription(event.target.value);

  const handleContentChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    // if (event.target.value.length <= CONTENT_MAX_LENGTH) {
    //   setContent(event.target.value);
    // }
    setContent(event.target.value);
    if (imageBase64) {
      setImageBase64(null); // Clear image base64 if user types text
    }
  };

  // file to base64 conversion
  // https://stackoverflow.com/questions/36280818/how-to-convert-file-to-base64-in-javascript by Dmitri Pavlutin
  // referenced on October 25-26, 2024
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        // dataURL format commonly looks like this --> data:[<mediatype>][;base64],<data>
        // remove metadata from the result, so we can get the base64-encoded data (the <data> part above).
        const base64String = reader.result?.toString().replace(/^data:.+;base64,/, "") || "";
        setImageBase64(base64String);
        setContent("");
        setFileName(file.name);
        console.log("Uploaded Image in Base64:", base64String);

        file.type === "image/png" ? setContentType("image/png;base64") :
        file.type === "image/jpeg" ? setContentType("image/jpeg;base64") :
        setContentType("application/base64");
      };
      reader.readAsDataURL(file); // Convert to base64
    }
  };

  const handleCombinedClick = async () => {
    try {
      console.log(authProvider.isAuthenticated);
      if (!authProvider.isAuthenticated) {
        console.error("User not loaded yet.");
        return;
      }

      // First request: Create a new post
      const visibilityNumber = getVisibilityNumber(
        activeIcon.toUpperCase() as VisibilityChoices
      );

      const newPost = {
        type: "post",
        title: title,
        description: description,
        contentType: imageBase64 ? contentType : "text/plain", // or markdown
        content: imageBase64 || content,
        published: new Date().toISOString(),
        visibility: visibilityNumber,
      };

      console.log("Need to know what newPost is: ", newPost);

      const postResponse = await api.post<Post>(
        `/api/authors/${authProvider.user.uuid}/posts/`,
        newPost
      );
      console.log("Post successfully created:", postResponse.data);

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
      if (visibilityNumber === 1 || visibilityNumber === 3) {
        for (const follower of uniqueFollowers) {
          const inboxUrl = `/api/authors/${follower.id}/inbox/`;
          try {
            const inboxResponse = await api.post<{ message: string }>(
              inboxUrl,
              postResponse.data
            );
            console.log(inboxResponse.data);
          } catch (error) {
            console.error(
              `Error sending post to inbox of ${follower.id}:`,
              error
            );
          }
        }
        console.log("All posts sent to followers' inboxes.");
      }

      // Friends receive inbox on all type of post
      for (const friend of friends) {
        const inboxUrl = `/api/authors/${friend.id}/inbox/`;
        try {
          const inboxResponse = await api.post<{ message: string }>(
            inboxUrl,
            postResponse.data
          );
          console.log(inboxResponse.data);
        } catch (error) {
          console.error(
            `Error sending post to friend's inbox of ${friend.id}:`,
            error
          );
        }
      }
      console.log("All posts sent to followers/friends' inboxes.");


      // Close the input modal and reset input fields
      setShowDetail(false)
      setTitle("")
      setDescription("")
      setContent("")
      setImageBase64(null); // Clear image base64 on post submission

    } catch (error) {
      console.error("Error in combined request flow:", error);
    }
  };

  const isPostDisabled = title.length === 0 || (!content && !imageBase64);

  if (!authProvider.isAuthenticated) {
    return <></>;
  }

  return (
    <div className={styles.container} ref={postBarRef}>
      <section className={styles["post-bar"]} onClick={handleInputClick}>
        <img
          src={
            authProvider.user.profileImage ??
            `https://ui-avatars.com/api/?background=random&name=${author.displayName}`
          }
          alt="User"
          className={styles["user-image"]}
        />
        <div className={styles["vertical-divider"]}></div>
        <span
         className={styles["post-input"]}
       > Click To Start Your Post</span>
        <button
          className={styles["add-button"]}
          onClick={() => document.getElementById("image-upload")?.click()}
        >
          <span>+</span>
        </button>
        <input
          type="file"
          accept="image/png, image/jpeg"
          id="image-upload"
          style={{ display: "none" }}
          onChange={handleFileUpload}
        />
      </section>

      {(showDetail) && (
        <div className={styles["detail-container"]}>
         <label className={styles["input-label"]}>Title</label>
         <textarea
           className={styles["description-input"]}
           placeholder="Start your post with a title"
           value={title}
           onChange={handleTitleChange}
         />

          <label className={styles["input-label"]}>Description</label>
          <textarea
            className={styles["description-input"]}
            placeholder="Add a brief description..."
            value={description}
            onChange={handleDescriptionChange}
          />

          {imageBase64 ? (
            <div className={styles["image-preview"]}>
              <p>Uploaded: {fileName}</p>
              <img
                src={`data:image/png;base64,${imageBase64}`}
                alt="Preview"
                className={styles["uploaded-image"]}
              />
            </div>
          ) : (
            <>
              <label className={styles["input-label"]}>Content</label>
              <textarea
                className={styles["content-input"]}
                placeholder="Write your post content here..."
                value={content}
                onChange={handleContentChange}
              />
            </>
          )}
        </div>
      )}

      {(showDetail) && (
        <section className={styles["button-bar"]}>
          <div className={styles["left-bar"]}>
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
                activeIcon === "unlisted" ? styles.active : ""
              }`}
              onClick={() => handleIconClick("unlisted")}
            >
              <i className={`${styles.icon} ${styles["link-icon"]}`}></i>
            </div>
          </div>
          <button className={`${styles["mark-button"]} ${activeCommonMark ? styles.active : ""}`} onClick={() => setActiveCommonMark(!activeCommonMark)}>
              Markdown
          </button>
          </div>
          <button
            className={styles["post-button"]}
            onClick={handleCombinedClick}
            disabled={isPostDisabled}
          >
            Post
          </button>
        </section>
      )}
    </div>
  );
};

export default PostBar;
