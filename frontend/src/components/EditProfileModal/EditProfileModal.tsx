import React, { useEffect } from "react";
import Modal from "react-modal";
import TextField from "@mui/material/TextField";
import styled from "@mui/material/styles/styled";

import styles from "./EditProfileModal.module.scss";

// Styling inspired from https://medium.com/@irwantoalvin/how-to-style-your-material-ui-textfield-integrate-it-with-react-hook-form-and-make-it-reusable-0f3050a90e9a, Downloaded 2024-10-24
// need to style field like this otherwise stylings may reset and not appear properly
const StyledInputTextField = styled(TextField)({
  "& label": {
    color: "#70ffaf !important",
  },

  "& input": {
    color: "white !important",
  },

  // style the outline of the input field
  ".MuiOutlinedInput-notchedOutline": {
    borderColor: "white !important",
  },

  // style helper text
  "& .MuiFormHelperText-root": {
    color: "#70ffaf",

    // style error helper text
    "&.Mui-error": {
      color: "#ff7070",
    },
  },
});

interface EditProfileModalProps {
  isOpen: boolean;
  onSave: (profileData: { displayName: string; githubLink: string }) => void;
  author: any; //contains all the author data
  onClose: () => void;
}

const EditUserProfile: React.FC<EditProfileModalProps> = ({
  isOpen,
  author,
  onSave,
  onClose,
}) => {
  console.log(author);
  const [displayName, setDisplayName] = React.useState("");
  const [githubLink, setGithubLink] = React.useState("");
  const [isDisplayNameError, setIsDisplayNameError] = React.useState(false);
  const [isGithubLinkError, setIsGithubLinkError] = React.useState(false);
  const [displayNameErrorMsg, setDisplayNameErrorMsg] = React.useState("");
  const [githubLinkErrorMsg, setGithubLinkErrorMsg] = React.useState("");
  const [isSubmitDisabled, setIsSubmitDisabled] = React.useState(false);

  const MAX_DISPLAYNAME_LENGTH = 20;

  useEffect(() => {
    console.log(`Author data: ${author}`);
    setDisplayName(author.displayName);
    setGithubLink(author.github);

    if (displayName.length == MAX_DISPLAYNAME_LENGTH) {
      setIsDisplayNameError(true);
      setIsSubmitDisabled(false);
      setDisplayNameErrorMsg(
        `You've reached the max character limit of ${MAX_DISPLAYNAME_LENGTH}`
      );
    } else {
      setIsDisplayNameError(false);
      setIsSubmitDisabled(false);
      setDisplayNameErrorMsg("");
    }
  }, [author, isOpen]);

  const validateDisplayName = (e) => {
    setDisplayName(e.target.value);
    if (e.target.value.length == MAX_DISPLAYNAME_LENGTH) {
      setIsDisplayNameError(true);
      setIsSubmitDisabled(false);
      setDisplayNameErrorMsg(
        `You've reached the max character limit of ${MAX_DISPLAYNAME_LENGTH}`
      );
    } else if (e.target.value.length === 0) {
      setIsDisplayNameError(true);
      setIsSubmitDisabled(true);
      setDisplayNameErrorMsg("Display name cannot be empty");
    } else {
      setIsDisplayNameError(false);
      setIsSubmitDisabled(false);
      setDisplayNameErrorMsg("");
    }
  };

  const validateGithubLink = (e) => {
    setGithubLink(e.target.value);
    if (e.target.value.length === 0) {
      setIsGithubLinkError(true);
      setIsSubmitDisabled(true);
      setGithubLinkErrorMsg("Github link cannot be empty");
    }
    // From chatGPT, "regex statement to check if the link starts with `https://github.com/`", Downloaded 2024-10-25
    // check if the link starts with https://github.com/
    else if (!e.target.value.match(/^https:\/\/github\.com\//)) {
      setIsGithubLinkError(true);
      setIsSubmitDisabled(true);
      setGithubLinkErrorMsg("Invalid Github link");
    } else {
      setIsGithubLinkError(false);
      setIsSubmitDisabled(false);
      setGithubLinkErrorMsg("");
    }
  };

  const handleSave = () => {
    console.log(`Saving profile data: ${displayName}, ${githubLink}`);
    onSave({ displayName, githubLink });
    onClose(); // close modal
  };

  return (
    <Modal
      isOpen={isOpen}
      className={styles.modal}
      overlayClassName={styles.overlay}
    >
      <div className={styles.container}>
        <h1>Edit Profile</h1>
        <div className={styles.form}>
          <div className={styles.inputContainer}>
            <StyledInputTextField
              label="Display Name"
              placeholder="Enter a display name ..."
              onChange={validateDisplayName}
              value={displayName}
              inputProps={{ maxLength: MAX_DISPLAYNAME_LENGTH }}
              error={isDisplayNameError}
              helperText={displayNameErrorMsg}
            />
          </div>
          <div className={styles.inputContainer}>
            <StyledInputTextField
              label="Github Link"
              placeholder="Enter a Github link ..."
              onChange={validateGithubLink}
              value={githubLink}
              error={isGithubLinkError}
              helperText={githubLinkErrorMsg}
            />
          </div>
          <div className={styles.buttonContainer}>
            <button onClick={onClose} className={styles.cancel}>
              Cancel
            </button>
            <button
              onClick={handleSave}
              className={styles.save}
              disabled={isSubmitDisabled}
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default EditUserProfile;
