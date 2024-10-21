import React, { useState, useEffect } from "react";
import Modal from "react-modal";
import styles from "./EditPostModal.module.scss";

interface EditPostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: {
    title: string;
    content: string;
  } | null; // Allow post to be null or undefined
  onSubmit: (updatedPost: { title: string; content: string }) => void;
}

export default function EditPostModal({
  isOpen,
  onRequestClose,
  post,
  onSubmit,
}: EditPostModalProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  // Ensure that modal fields reset when `post` data changes
  useEffect(() => {
    if (post) {
      // Check if post is defined
      setTitle(post.title);
      setContent(post.content);
    }
  }, [post]);

  const handleSave = () => {
    if (post) {
      // Ensure post is defined before saving
      onSubmit({ title, content });
    }
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
