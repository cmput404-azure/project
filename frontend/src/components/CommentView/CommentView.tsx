import React from "react";
import Modal from "react-modal";
import styles from "./CommentView.module.scss";
import PostBar from "../PostBar/PostBar";

interface Comment {
  id: number;
  image: string;
  author: string;
  timePosted: string;
  text: string;
}

interface CommentViewProps {
  isOpen: boolean;
  onRequestClose: () => void;
  postComponent: React.ReactNode;
  comments: Comment[]; // List of comments
}

const CommentView: React.FC<CommentViewProps> = ({
  isOpen,
  onRequestClose,
  postComponent,
  comments,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modalContent}
      overlayClassName={styles.modalOverlay}
    >
      {/* Post Component */}
      <div className={styles.post}>{postComponent}</div>

      <section className={styles.comments}>
        <div className={styles.commentsHeader}>Comments</div>

        {/* Comments Section */}
        <div className={styles.commentsSection}>
          {comments.map((comment) => (
            <div key={comment.id} className={styles.comment}>
              <div key={comment.id} className={styles.comment}>
                <img
                  src={comment.image}
                  alt={comment.author}
                  className={styles.userImage}
                />
              </div>
              <div className={styles.commentContent}>
                <div className={styles.authorTime}>
                  <div className={styles.commentAuthor}>{comment.author}</div>
                  <div className={styles.timePosted}>{comment.timePosted}</div>
                </div>
                <div className={styles.commentText}>{comment.text}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Comment Section */}
      <div className={styles.commentBar}>
        <PostBar
          userImage="https://via.placeholder.com/50"
          showButtonBar={false}
        />
      </div>
    </Modal>
  );
};

export default CommentView;
