import Modal from "react-modal";
import React from "react";
import styles from "./CommentView.module.scss";
import TextField from "@mui/material/TextField";
import { useState } from "react";

const CommentInputField = ({ author }) => {
  const [commentFieldClicked, setCommentFieldClicked] = useState(false);

  const handleCommentFieldClick = () => {
    setCommentFieldClicked(true);
  };

  const handleCommentFieldCancel = () => {
    setCommentFieldClicked(false);
  };

  return (
    <section className={styles.commentInput}>
      <div className={styles.commentDisplay}>
        <div className={styles.userImageContainer}>
          <img
            className={styles.userImage}
            src={`https://ui-avatars.com/api/?background=random&name=${author}`}
            alt="User Profile"
          />
        </div>
        <div className={styles.textFieldContainer}>
          <TextField
            className={styles.commentInputField}
            label="Add a comment"
            placeholder="Add a comment..."
            variant="standard"
            // From https://stackoverflow.com/questions/45939909/put-length-constraint-in-a-textfield-in-react-js, Downloaded 2024-10-24
            inputProps={{ maxLength: 50 }} // MUI docs says thsi will be deprecated eventually, but works for now
            helperText="Max 50 characters"
            // Styling inspired from https://muhimasri.com/blogs/mui-textfield-colors-styles/, Downloaded 2024-10-24
            sx={{
              input: { color: "white" },
              "& .MuiInputLabel-root": { color: "white" },
              "& .MuiInput-underline:before": { borderBottomColor: "white" },
              "& .MuiInput-underline:hover:before": {
                borderBottomColor: "white",
              },
              "& .MuiInput-underline:hover": {
                borderBottomColor: "white",
              },
              "& .MuiInput-underline:hover:after": {
                borderBottomColor: "white",
              },
              "& .MuiInput-underline:after": { borderBottomColor: "white" },
              "& .MuiFormHelperText-root": { color: "white" },
            }}
            onClick={handleCommentFieldClick}
          />
        </div>
      </div>
      {commentFieldClicked && (
        <div className={styles.commentButtonContainer}>
          <button
            className={styles.cancelButton}
            onClick={handleCommentFieldCancel}
          >
            cancel
          </button>
          <button className={styles.postButton}>Post</button>
        </div>
      )}
    </section>
  );
};

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
  author: string;
}

const CommentView: React.FC<CommentViewProps> = ({
  isOpen,
  onRequestClose,
  postComponent,
  comments,
  author,
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
          <CommentInputField author={author} />
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
    </Modal>
  );
};

export default CommentView;
