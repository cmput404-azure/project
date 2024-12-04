import Avatar from "@mui/material/Avatar";
import TextField from "@mui/material/TextField";
import inbox from "../../service/inbox";
import profileService from "../../service/profile";
import styled from "@mui/material/styles/styled";
import styles from "./CommentInput.module.scss";
import { useState } from "react";

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

const CommentInputField = ({ authorObj, post, onCommentAdded }) => {
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

  const handleCommentSubmit = async (authorObj: any) => {
    const comment_obj = {
      type: "comment",
      author: authorObj,
      comment: textInField,
      post: post.id,
    };

    const response = await inbox.sendCommentToInbox(
      post.author.id,
      comment_obj
    );

    if (response) {
      // In here  you will append the comment to the list. You can create a useState hook and then call something set comments
      onCommentAdded(response);
    }

    // Reset to initial states
    setTextInField("");
    setCommentFieldClicked(false);
    setIsTextError(false);
    setDisableCommentButton(true);
    setTextErrorMsg("");
  };

  // Inspired from https://muhimasri.com/blogs/mui-validation/, Downloaded 2024-10-24
  const handleTextInput = (e) => {
    setTextInField(e.target.value);
    if (e.target.value.length === MAX_CHARACTERS) {
      setIsTextError(true);
      setTextErrorMsg(
        `You've reached the max character limit of ${MAX_CHARACTERS}`
      );
    } else if (e.target.value.length === 0) {
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
          <div className="avatar">
            <Avatar
              src={profileService.getProfilePicture(authorObj)}
              alt={authorObj.author?.displayName}
            />
          </div>
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
            inputProps={{ maxLength: MAX_CHARACTERS }} // MUI docs says this will be deprecated eventually, but works for now
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
