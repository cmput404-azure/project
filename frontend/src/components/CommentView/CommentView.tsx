import Modal from "react-modal";
import React from "react";
import styles from "./CommentView.module.scss";
import TextField from "@mui/material/TextField";
import { useState } from "react";

const CommentInputField = ({ authorDisplayName }) => {
  const [commentFieldClicked, setCommentFieldClicked] = useState(false);
  const [isTextError, setIsTextError] = useState<boolean>(false);
  const [textErrorMsg, setTextErrorMsg] = useState("");
  const [textInField, setTextInField] = useState("");

  const MAX_CHARACTERS = 50; // toggles the max amount of characters allowed in a comment

  const handleCommentFieldClick = () => {
    setCommentFieldClicked(true);
  };

  const handleCommentFieldCancel = () => {
    setCommentFieldClicked(false);
    setIsTextError(false);
    setTextErrorMsg("");
    setTextInField("");
  };

  const handleCommentSubmit = () => {
    console.log(`Comment: "${textInField}" | Submitted`); // for testing, change to API call or whatever
  };

  // Inspired from https://muhimasri.com/blogs/mui-validation/, Downloaded 2024-10-24
  const handleTextInput = (e) => {
    setTextInField(e.target.value);
    if (e.target.value.length == MAX_CHARACTERS) {
      setIsTextError(true);
      setTextErrorMsg(
        `Comment must be less than ${MAX_CHARACTERS} characters long`
      );
    } else {
      setIsTextError(false);
      setTextErrorMsg(`Max ${MAX_CHARACTERS} characters`);
    }
  };

  return (
    <section className={styles.commentInput}>
      <div className={styles.commentDisplay}>
        <div className={styles.userImageContainer}>
          <img
            className={styles.userImage}
            src={`https://ui-avatars.com/api/?background=random&name=${authorDisplayName}`}
            alt="User Profile"
          />
        </div>
        <div className={styles.textFieldContainer}>
          <TextField
            className={styles.commentInputField}
            label="Add a comment"
            placeholder="Type your comment..."
            variant="standard"
            // Styling inspired from https://muhimasri.com/blogs/mui-textfield-colors-styles/, Downloaded 2024-10-24
            sx={{
              input: { color: "#fff" },
              "& .MuiInputLabel-root": { color: "#fff" },
              "& .MuiInput-underline": { borderBottomColor: "#fff" },
              "& .MuiInput-underline:before": { borderBottomColor: "#fff" },
              "& .MuiInput-underline:hover:before": {
                borderBottomColor: "#fff",
              },
              "& .MuiInput-underline:hover": {
                borderBottomColor: "#fff",
              },
              "& .MuiInput-underline:hover:after": {
                borderBottomColor: "#fff",
              },
              "& .MuiInput-underline:after": { borderBottomColor: "#fff" },
              "& .MuiFormHelperText-root": { color: "#fff" },
            }}
            onClick={handleCommentFieldClick}
            onChange={handleTextInput}
            // From https://stackoverflow.com/questions/45939909/put-length-constraint-in-a-textfield-in-react-js, Downloaded 2024-10-24
            inputProps={{ maxLength: MAX_CHARACTERS }} // MUI docs says thsi will be deprecated eventually, but works for now
            error={isTextError}
            helperText={textErrorMsg}
            value={textInField}
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
          <button className={styles.postButton} onClick={handleCommentSubmit}>
            Comment
          </button>
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
  author: any; // author object
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
          <CommentInputField authorDisplayName={author.username} />
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
