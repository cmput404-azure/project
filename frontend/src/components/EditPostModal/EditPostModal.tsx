import React, { useState, useEffect } from "react";
import Modal from "react-modal";
import styles from "./EditPostModal.module.scss";
import Box from "@mui/material/Box";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";

interface EditPostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: {
    title: string;
    content: string;
    visibility: number;
  } | null; // Allow post to be null or undefined
  onSubmit: (updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) => void;
}

export default function EditPostModal({
  isOpen,
  onRequestClose,
  post,
  onSubmit,
}: EditPostModalProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<number>(0);

  // Ensure that modal fields reset when `post` data changes
  useEffect(() => {
    if (post) {
      // Check if post is defined
      setTitle(post.title);
      setContent(post.content);
      setVisibility(post.visibility);
    }
  }, [post]);

  const handleSave = () => {
    if (post) {
      // Ensure post is defined before saving
      onSubmit({ title, content, visibility });
      onRequestClose(); // close modal after saving
    }
  };

  const handleVisibilityChange = (event: SelectChangeEvent<number>) => {
    setVisibility(event.target.value as number); // Cast the value to number
  };

  if (!post) {
    return null; // Return null if post data is unavailable to prevent rendering errors
  }

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modal}
      overlayClassName={styles.overlay}
    >
      <h2 className={styles.title}>Edit Post</h2>
      <form>
        <div className={styles.formGroup}>
          <label htmlFor="postTitle">Title</label>
          <input
            id="postTitle"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="postContent">Content</label>
          <textarea
            id="postContent"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <div className={styles.formGroup}>
          <FormControl fullWidth>
            <InputLabel className={styles.visibilitySelectLabelTitle}>
              Visibility
            </InputLabel>
            <Select
              className={styles.visibilitySelectLabel}
              labelId="visibility-select-label"
              value={visibility}
              label="Visibility"
              onChange={handleVisibilityChange}
            >
              <MenuItem value={0}>Public</MenuItem>
              <MenuItem value={1}>Friends-Only</MenuItem>
              <MenuItem value={2}>Unlisted</MenuItem>
            </Select>
          </FormControl>
        </div>
        <div className={styles.buttonGroup}>
          <button
            type="button"
            onClick={handleSave}
            className={styles.saveButton}
          >
            Save
          </button>
          <button
            type="button"
            onClick={onRequestClose}
            className={styles.cancelButton}
          >
            Cancel
          </button>
        </div>
      </form>
    </Modal>
  );
}
