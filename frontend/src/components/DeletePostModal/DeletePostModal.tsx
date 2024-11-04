import React from "react";
import Modal from "react-modal";

import styles from "./DeletePostModal.module.scss";

interface DeletePostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  onDelete: () => void;
}

const DeletePostModal: React.FC<DeletePostModalProps> = ({
  isOpen,
  onRequestClose,
  onDelete,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modalContent}
      overlayClassName={styles.modalOverlay}
    >
      <div className={styles.modal}>
        <h2>Are you sure you want to delete this post?</h2>
        <div className={styles.buttons}>
          <button onClick={onRequestClose} className={styles.cancelButton}>
            Cancel
          </button>
          <button onClick={onDelete} className={styles.deleteButton}>
            Delete
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default DeletePostModal;
