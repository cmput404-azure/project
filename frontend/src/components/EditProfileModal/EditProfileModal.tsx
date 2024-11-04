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
  const [displayName, setDisplayName] = React.useState("");
  const [githubLink, setGithubLink] = React.useState("");
  const [isDisplayNameError, setIsDisplayNameError] = React.useState(false);
  const [isGithubLinkError, setIsGithubLinkError] = React.useState(false);
  const [displayNameErrorMsg, setDisplayNameErrorMsg] = React.useState("");
  const [githubLinkErrorMsg, setGithubLinkErrorMsg] = React.useState("");
  const [isSubmitDisabled, setIsSubmitDisabled] = React.useState(false);
  const [isDisplayNameValid, setIsDisplayNameValid] = React.useState(false);
  const [isGithubLinkValid, setIsGithubLinkValid] = React.useState(false);

  const MAX_DISPLAYNAME_LENGTH = 20;

  const validateDisplayName = (value) => {
    if (value.length == MAX_DISPLAYNAME_LENGTH) {
      setIsDisplayNameError(true);
      setDisplayNameErrorMsg(
        `You've reached the max character limit of ${MAX_DISPLAYNAME_LENGTH}`
      );
      return true; // there is no error
    } else if (value.length === 0) {
      setIsDisplayNameError(true);
      setDisplayNameErrorMsg("Display name cannot be empty");
      return false; // there is an error
    } else {
      setIsDisplayNameError(false);
      setDisplayNameErrorMsg("");
      return true; // there is no error
    }
  };

  const validateGithubLink = (value) => {
    if (value.length == 0) {
      setIsGithubLinkError(true);
      setGithubLinkErrorMsg("Github link cannot be empty");
      return false; // there is an error
    }
    // From chatGPT, "regex statement to check if the link starts with `https://github.com/`", Downloaded 2024-10-25
    // check if the link starts with https://github.com/
    else if (!value.match(/^https:\/\/github\.com\//)) {
      setIsGithubLinkError(true);
      setGithubLinkErrorMsg(
        `Invalid Github link, link must begin with "https://github.com/"`
      );
      return false; // there is an error
    } else {
      setIsGithubLinkError(false);
      setGithubLinkErrorMsg("");
      return true; // there is no error
    }
  };

  useEffect(() => {
    setDisplayName(author.displayName);
    setGithubLink(author.github);

    const isDisplayNameValid = validateDisplayName(displayName);
    setIsDisplayNameValid(isDisplayNameValid);
    const isGithubLinkValid = validateGithubLink(githubLink);
    setIsGithubLinkValid(isGithubLinkValid);
    setIsSubmitDisabled(!isDisplayNameValid || !isGithubLinkValid);
  }, [author, isOpen]);

  const handleDisplayNameChange = (e) => {
    const value = e.target.value;
    setDisplayName(value);
    const isDisplayNameValid = validateDisplayName(value);
    setIsDisplayNameValid(isDisplayNameValid);
    setIsSubmitDisabled(!isDisplayNameValid || !isGithubLinkValid);
  };

  const handleGithubLinkChange = (e) => {
    const value = e.target.value;
    setGithubLink(value);
    const isGithubLinkValid = validateGithubLink(value);
    setIsGithubLinkValid(isGithubLinkValid);
    setIsSubmitDisabled(!isDisplayNameValid || !isGithubLinkValid);
  };

  const handleSave = () => {
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
              onChange={handleDisplayNameChange}
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
              onChange={handleGithubLinkChange}
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
