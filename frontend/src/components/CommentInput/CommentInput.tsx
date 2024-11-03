import { useState } from "react";
import TextField from "@mui/material/TextField";
import styled from "@mui/material/styles/styled";
import styles from "./CommentInput.module.scss";

// Styling inspired from https://medium.com/@irwantoalvin/how-to-style-your-material-ui-textfield-integrate-it-with-react-hook-form-and-make-it-reusable-0f3050a90e9a, Downloaded 2024-10-24
// need to style field like this otherwise stylings may reset and not appear properly
const StyledCommentInputField = styled(TextField)({
  "& label": {
    color: "#ffffff !important",
  },

  "& input": {
    color: "white !important",
  },

  // style underline
  "& .MuiInput-underline:before": {
    borderBottomColor: "white !important",
  },

  "& .MuiInput-underline:after": {
    borderBottomColor: "white !important",
  },

  // style helper text
  "& .MuiFormHelperText-root": {
    color: "#ffffff",

    // style error helper text
    "&.Mui-error": {
      color: "#dc3545",
    },
  },
});

const CommentInputField = ({ authorObj }) => {
  const [commentFieldClicked, setCommentFieldClicked] = useState(false);
  const [isTextError, setIsTextError] = useState<boolean>(false);
  const [textErrorMsg, setTextErrorMsg] = useState("");
  const [textInField, setTextInField] = useState("");
  const [disableCommentButton, setDisableCommentButton] = useState(true);

  const MAX_CHARACTERS = 500; // Max comment toggle

  const handleCommentFieldClick = () => {
    setCommentFieldClicked(true);
  };

  const handleCommentFieldCancel = () => {
    setCommentFieldClicked(false);
    setIsTextError(false);
    setTextErrorMsg("");
    setTextInField("");
  };

  const handleCommentSubmit = (authorObj: any) => {
    console.log(`AuthorID: ${authorObj.id}`); // for testing, change to API call or whatever
    console.log(`Author: ${authorObj.displayName}`); // for testing, change to API call or whatever
    console.log(`Comment: "${textInField}" | Submitted`); // for testing, change to API call or whatever
  };

  // Inspired from https://muhimasri.com/blogs/mui-validation/, Downloaded 2024-10-24
  const handleTextInput = (e) => {
    setTextInField(e.target.value);
    if (e.target.value.length == MAX_CHARACTERS) {
      setIsTextError(true);
      setTextErrorMsg(
        `You've reached the max character limit of ${MAX_CHARACTERS}`
      );
    } else if (e.target.value.length == 0) {
      setIsTextError(true);
      setDisableCommentButton(true);
      setTextErrorMsg("Comment cannot be empty");
    } else {
      setIsTextError(false);
      setDisableCommentButton(false);
      setTextErrorMsg(
        `${e.target.value.length}/${MAX_CHARACTERS} characters used`
      );
    }
  };

  return (
    <section className={styles.commentInput}>
      <div className={styles.commentDisplay}>
        <div className={styles.userImageContainer}>
          <img
            className={styles.userImage}
            src={`https://ui-avatars.com/api/?background=random&name=${authorObj.displayName}`}
            alt="User Profile"
          />
        </div>
        <div className={styles.textFieldContainer}>
          <StyledCommentInputField
            className={styles.commentInputField}
            label="Add a comment"
            placeholder="Type your comment..."
            variant="standard"
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
          <button
            className={styles.commentButton}
            disabled={disableCommentButton}
            onClick={() => handleCommentSubmit(authorObj)}
          >
            Comment
          </button>
        </div>
      )}
    </section>
  );
};

export default CommentInputField;
