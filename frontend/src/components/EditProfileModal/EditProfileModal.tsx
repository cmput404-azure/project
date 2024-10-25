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

  useEffect(() => {
    console.log(`Author data: ${author}`);
    setDisplayName(author.displayName);
    setGithubLink(author.github);
  }, [author]);

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
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>
          <div className={styles.inputContainer}>
            <StyledInputTextField
              label="Github Link"
              value={githubLink}
              onChange={(e) => setGithubLink(e.target.value)}
            />
          </div>
          <div className={styles.buttonContainer}>
            <button onClick={onClose} className={styles.cancel}>
              Cancel
            </button>
            <button onClick={handleSave} className={styles.save}>
              Save
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default EditUserProfile;
