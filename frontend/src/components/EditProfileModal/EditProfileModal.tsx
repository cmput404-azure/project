import React, { useEffect } from "react";
import Modal from "react-modal";
import TextField from "@mui/material/TextField";

import styles from "./EditProfileModal.module.scss";

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
            <TextField
              label="Display Name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>
          <div className={styles.inputContainer}>
            <TextField
              label="Github Link"
              value={githubLink}
              onChange={(e) => setGithubLink(e.target.value)}
            />
          </div>
          <div className={styles.buttonContainer}>
            <button onClick={onClose}>Cancel</button>
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default EditUserProfile;
