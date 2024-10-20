import React, { useState } from "react";
import Modal from "react-modal";
import styles from "./EditPostModal.module.scss";

interface EditPostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: {
    title: string;
    content: string;
  };
  onSubmit: (updatedPost: { title: string; content: string }) => void;
}

export default function EditPostModal({
  isOpen,
  onRequestClose,
  post,
  onSubmit,
}: EditPostModalProps) {
  const [title, setTitle] = useState(post.title);
  const [content, setContent] = useState(post.content);

  const handleSave = () => {
    onSubmit({ title, content });
  };

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
