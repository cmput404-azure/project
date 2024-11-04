import Modal from "react-modal";
import React from "react";
import styles from "./CommentView.module.scss";
import Post from "../Post/Post";
import { PostData as PostModel } from "../../models/models";

interface CommentViewProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: PostModel;
}

const CommentView: React.FC<CommentViewProps> = ({
  isOpen,
  onRequestClose,
  post,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modalContent}
      overlayClassName={styles.modalOverlay}
    >
      <Post postGiven={post} canToggleComments={false} />
    </Modal>
  );
};

export default CommentView;
