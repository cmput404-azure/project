import { Avatar, CircularProgress, TextField, Tooltip } from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { VisibilityChoices, getVisibilityNumber } from "../../models/modelTypes";

import AddIcon from '@mui/icons-material/Add';
import EditNoteIcon from '@mui/icons-material/EditNote';
import LinkIcon from '@mui/icons-material/Link';
import PeopleIcon from '@mui/icons-material/People';
import { PostData as Post } from "../../models/models";
import PublicIcon from '@mui/icons-material/Public';
import { api } from "../../service/config";
import follow from "../../service/follow";
import inbox from "../../service/inbox";
import { normalizeURL } from "../../util/formatting/normalizeURL";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";
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
  const postBarRef = useRef<HTMLDivElement>(null); // Ref for the component
  const [activeIcon, setActiveIcon] = useState<IconType>("public");
  const [title, setTitle] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [activeCommonMark, setActiveCommonMark] = useState(false);
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [contentType, setContentType] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const isPostDisabled = title.length === 0 || (!content && !imageBase64);
  const authProvider = useAuth();

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

        file.type === "image/png" ? setContentType("image/png;base64") :
          file.type === "image/jpeg" ? setContentType("image/jpeg;base64") :
            setContentType("application/base64");
      };
      reader.readAsDataURL(file); // Convert to base64
    }
  };

  const handleCombinedClick = async () => {
    try {
      if (!authProvider.isAuthenticated) {
        return;
      }
      setIsLoading(true);

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

      const postResponse = await api.post<Post>(
        `/api/authors/${authProvider.user.uuid}/posts/`,
        newPost
      );

      // Get friends and followers list, followers include both friends and followers
      const followers = await follow.getFollowers(authProvider.user.uuid);
      const friends = await follow.getFriends(authProvider.user.uuid);

      // Send to followers if post is public or unlisted
      if (normalizeVisibility(visibilityNumber) === 1 || normalizeVisibility(visibilityNumber) === 3) {
        for (const follower of followers) {
          if (normalizeURL(follower.host) === normalizeURL(process.env.REACT_APP_API_BASE_URL)) {
            await inbox.sendPostToInbox(follower.id, postResponse.data);
          } else {
            const enrichedPost = { // to handle remote followers
              ...postResponse.data,
              follower: {
                type: "author",
                id: follower.id,
                host: follower.host,
                displayName: follower.displayName,
                page: follower.page,
                github: follower.github,
                profileImage: follower.profileImage
              }
            };
            await inbox.sendPostToInbox(follower.id, enrichedPost);
          }
        }
      } else {
        for (const friend of friends) {
          if (normalizeURL(friend.host) === normalizeURL(process.env.REACT_APP_API_BASE_URL)) {
            await inbox.sendPostToInbox(friend.id, postResponse.data);
          } else {
            const enrichedPost = { // to handle remote followers
              ...postResponse.data,
              follower: {
                type: "author",
                id: friend.id,
                host: friend.host,
                displayName: friend.displayName,
                page: friend.page,
                github: friend.github,
                profileImage: friend.profileImage
              }
            };
            await inbox.sendPostToInbox(friend.id, enrichedPost);
          }
        }
      }
      // re-fetch stream
      fetchPosts();
      
      // Close the input modal and reset input fields
      setIsLoading(false);
      setShowDetail(false);
      setTitle("");
      setDescription("");
      setContent("");
      setImageBase64(null); // Clear image base64 on post submission
      setActiveCommonMark(false);
      setActiveIcon("public");

    } catch (error) {
      console.error("Error in combined request flow:", error);
    }
  };

  if (!authProvider.isAuthenticated) {
    return <></>;
  }

  return (
    <div className={styles.container} ref={postBarRef} style={{ backgroundColor: showDetail ? "#777" : "transparent" }}>
      <section className={styles.post_bar} onClick={handleInputClick}>
        <div className="avatar">
          <Avatar
            src={
              authProvider.user.profileImage && authProvider.user.profileImage !== "" ?
              authProvider.user.profileImage : 
              `https://ui-avatars.com/api/?background=random&name=${author.displayName}`
            }
            alt="User"
            className={styles.user_image}
          />
        </div>
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
          <AddIcon  />
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
              <img
                src={`data:image/png;base64,${imageBase64}`}
                alt="Preview"
                className={styles.uploaded_image}
              />
              <p>Uploaded: {fileName}</p>
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
                className={`${styles.icon_section} ${activeIcon === "public" ? styles.active : ""}`}
                onClick={() => handleIconClick("public")}
              >
                <PublicIcon className={styles.icon}/>
              </div>
              <div className={styles.vertical_divider}></div>
              <div
                className={`${styles.icon_section} ${activeIcon === "friends" ? styles.active : ""}`}
                onClick={() => handleIconClick("friends")}
              >
                <PeopleIcon className={styles.icon}/>
              </div>
              <div className={styles.vertical_divider}></div>
              <div
                className={`${styles.icon_section} ${activeIcon === "unlisted" ? styles.active : ""}`}
                onClick={() => handleIconClick("unlisted")}
              >
                <LinkIcon className={styles.icon}/>
              </div>
            </div>
            <Tooltip title="toggle markdown">
              <button
                className={`${styles.mark_button} ${activeCommonMark ? styles.active : ""}`}
                onClick={() => setActiveCommonMark(!activeCommonMark)}
              >
                <EditNoteIcon className={styles.icon}/>
              </button>
            </Tooltip>
          </div>
          <button
            className={styles.post_button}
            onClick={handleCombinedClick}
            disabled={isPostDisabled}
          >
            {(isLoading) ? <CircularProgress size={24} sx={{ color: "#b0b0b0" }} /> : "Post"}
          </button>
        </section>
      )}
    </div>
  );
};

export default PostBar;