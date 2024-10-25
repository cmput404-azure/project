import React from "react";
import Modal from "react-modal";

import styles from "./EditProfileModal.module.scss";

interface EditProfileModalProps {
  isOpen: boolean;
  onSave: (profileData: {
    profileImage: string;
    displayName: string;
    githubLink: string;
  }) => void;
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
  const [profileImage, setProfileImage] = React.useState("");
  const [displayName, setDisplayName] = React.useState("");
  const [githubLink, setGithubLink] = React.useState("");

  const handleSave = () => {
    onSave({ profileImage, displayName, githubLink });
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
          <button onClick={handleSave}>Save</button>
        </div>
      </div>
    </Modal>
  );
};

export default EditUserProfile;
