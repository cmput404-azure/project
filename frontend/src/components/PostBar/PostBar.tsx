import { Author, PostData as Post } from "../../models/models";
import React, { useEffect, useRef, useState } from "react";
import { TextField, TextareaAutosize, Tooltip } from "@mui/material";
import {
  VisibilityChoices,
  getVisibilityNumber,
} from "../../models/modelTypes";

import EditNoteIcon from '@mui/icons-material/EditNote';
import LinkIcon from '@mui/icons-material/Link';
import PeopleIcon from '@mui/icons-material/People';
import PublicIcon from '@mui/icons-material/Public';
import { api } from "../../service/config";
import follow from "../../service/follow";
import inbox from "../../service/inbox";
import stream from "../../service/stream";
import styled from "@mui/material/styles/styled";
import styles from "./PostBar.module.scss";
import { useAuth } from "../../state";

interface PostBarProps {
  author?: any;
  fetchPosts: any;
}
type IconType = "public" | "friends" | "unlisted";

// Max character limits
const TITLE_MAX_LENGTH = 200;

const PostTextField = styled(TextField)({
  "& label": {
    color: "#ffffff !important",
  },

  "& input": {
    color: "white !important",
  },

  "& textarea": {
    color: "white !important",
  },

  "& .MuiOutlinedInput-root": {
    "& fieldset": {
      border: "none",
      boxShadow:"0 4px 7px rgba(0, 0, 0, 0.45)",
    },
    "&:hover fieldset": {
      border: "1px solid",
      borderColor: "white !important",
    },
    "&.Mui-focused fieldset": {
      border: "1px solid",
      borderColor: "#70ffaf !important",
    },
  },

  "& .MuiFormHelperText-root": {
    color: "#ffffff",
    "&.Mui-error": {
      color: "#dc3545",
    },
  },
});

const PostTitleField = styled(TextField)({
  "& label": {
    color: "#ffffff !important",
  },

  "& input": {
    color: "white !important",
  },

  "& .MuiInput-underline:before": {
    borderBottomColor: "white !important",
  },

  "& .MuiInput-underline:after": {
    borderBottomColor: "#70ffaf !important",
  },

  "& .MuiFormHelperText-root": {
    color: "#ffffff",

    "&.Mui-error": {
      color: "#dc3545",
    },
  },
});

const PostBar: React.FC<PostBarProps> = ({ fetchPosts, author }) => {
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
        contentType: imageBase64 ? contentType : activeCommonMark ? "text/markdown" : "text/plain",
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

      // Get friends and followers list, followers inlcude both friends and followers
      const followers = await follow.getFollowers(authProvider.user.uuid);
      const friends = await follow.getFriends(authProvider.user.uuid);

      // send to followers if post is public or unlisted
      // always send to friends for all type of posts
      if (visibilityNumber === 1 || visibilityNumber === 3) {
        for (const follower of followers) {
          const inboxResponse = await inbox.sendPostToInbox(follower.id, postResponse.data);
        }
      } else {
        for (const friend of friends) {
          const inboxResponse = await inbox.sendPostToInbox(friend.id, postResponse.data);
        }
      }

      // re-fetch stream
      fetchPosts();
      
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
    <div className={styles.container} ref={postBarRef} style={{ backgroundColor: showDetail ? "#777" : "transparent" }}>
      <section className={styles.post_bar} onClick={handleInputClick}>
        <img
          src={
            authProvider.user.profileImage ??
            `https://ui-avatars.com/api/?background=random&name=${author.displayName}`
          }
          alt="User"
          className={styles.user_image}
        />
        <div className={styles.vertical_divider}></div>
        <PostTitleField
          className={styles.post__input}
          fullWidth
          variant="standard"
          size="small"
          placeholder="Enter a title for your new post..."
          value={title}
          onChange={handleTitleChange}
          autoComplete='off'
        />
        <button
          className={styles.add_button}
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
        <div className={styles.detail_container}>
          <PostTextField
            className={styles.description_input}
            placeholder="Add a brief description..."
            multiline
            fullWidth
            value={description}
            onChange={handleDescriptionChange}
            
          />

          {imageBase64 ? (
            <div className={styles.image_preview}>
              <p>Uploaded: {fileName}</p>
              <img
                src={`data:image/png;base64,${imageBase64}`}
                alt="Preview"
                className={styles.uploaded_image}
              />
            </div>
          ) : (
            <>
              <PostTextField
                className={styles.content_input}
                multiline
                fullWidth
                placeholder="Write your post content here..."
                value={content}
                onChange={handleContentChange}
              />
            </>
          )}
        </div>
      )}

      {(showDetail) && (
        <section className={styles.button_bar}>
          <div className={styles.left_bar}>
            <div className={styles.icon_bar}>
              <div
                className={`${styles.icon_section} ${activeIcon === "public" ? styles.active : ""
                  }`}
                onClick={() => handleIconClick("public")}
              >
                <PublicIcon className={styles.icon}/>
              </div>
              <div className={styles.vertical_divider}></div>
              <div
                className={`${styles.icon_section} ${activeIcon === "friends" ? styles.active : ""
                  }`}
                onClick={() => handleIconClick("friends")}
              >
                <PeopleIcon className={styles.icon}/>
              </div>
              <div className={styles.vertical_divider}></div>
              <div
                className={`${styles.icon_section} ${activeIcon === "unlisted" ? styles.active : ""
                  }`}
                onClick={() => handleIconClick("unlisted")}
              >
                <LinkIcon className={styles.icon}/>
              </div>
            </div>
            <Tooltip title="toggle markdown">
              <button className={`${styles.mark_button} ${activeCommonMark ? styles.active : ""}`} onClick={() => setActiveCommonMark(!activeCommonMark)}>
                <EditNoteIcon className={styles.icon}/>
              </button>
            </Tooltip>
          </div>
          <button
            className={styles.post_button}
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
