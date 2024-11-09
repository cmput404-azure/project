import { Button, TextField } from "@mui/material";
import { useEffect, useState } from "react";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Modal from "react-modal";
import styled from "@mui/material/styles/styled";
import styles from "./EditPostModal.module.scss";

interface EditPostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: {
    title: string;
    content: string;
    visibility: number;
    contentType: string;
    description: string;
  } | null; // Allow post to be null or undefined
  onSubmit: (updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) => void;
}

const StyledFormControl = styled(FormControl)({
  "& .MuiInputLabel-root": {
    color: "#70ffaf !important",
  },
  "& .MuiSelect-root": {
    color: "white !important",
  },
  "& .MuiOutlinedInput-notchedOutline": {
    borderColor: "white !important",
  },
  "& .MuiSvgIcon-root": {
    color: "#70ffaf",
  },
});

export default function EditPostModal({
  isOpen,
  onRequestClose,
  post,
  onSubmit,
}: EditPostModalProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<number>(0);
  const [contentType, setContentType] = useState(`${post.contentType}`);
  console.log(post);
  console.log(post.contentType);
  console.log(contentType);
  // Ensure that modal fields reset when `post` data changes
  useEffect(() => {
    if (isOpen && post) {
      // Check if post is defined
      setTitle(post.title);
      setContent(post.content);
      setVisibility(post.visibility);
    }
  }, [isOpen, post]);

  const handleSave = () => {
    if (post) {
      // Ensure post is defined before saving
      onSubmit({ title, content, visibility });
      onRequestClose(); // close modal after saving
    }
  };

  const handleVisibilityChange = (event: SelectChangeEvent<number>) => {
    setVisibility(event.target.value as number); // Cast the value to number
  };

  if (!post) {
    return null; // Return null if post data is unavailable to prevent rendering errors
  }

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modal}
      overlayClassName={styles.overlay}
    >
      <h2 className={styles.title}>Edit Post</h2>
      <form>
        <div className={styles.formGroup}>
          <label>Title</label>
          <PostTextField
            value={title}
            fullWidth
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <div className={styles.formGroup}>
          <label>Content</label>
          {/^image\/(png|jpeg);base64$/.test(contentType) ? (
            <div className={styles.cardImage}>
              <img
                className={styles.postImage}
                src={`data:${contentType},${post.content}`}
                alt={post.description}
              />
            </div>
          ) : (
            <PostTextField
              className={styles.content_field}
              value={content}
              multiline
              fullWidth
              onChange={(e) => setContent(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                   padding: 0,
                },
                '& .MuiOutlinedInput-notchedOutline': {
                   border: 'none',
                },
                '& textarea': {
                  resize: 'none', // Remove resize handle
                },
             }}
            />
          )}
        </div>
        <div className={styles.formGroup}>
          <StyledFormControl fullWidth>
            <InputLabel className={styles.visibilitySelectLabelTitle}>
              Visibility
            </InputLabel>
            <Select
              className={styles.visibilitySelectLabel}
              labelId="visibility-select-label"
              value={visibility}
              label="Visibility"
              onChange={handleVisibilityChange}
            >
              <MenuItem value={1}>Public</MenuItem>
              <MenuItem value={2}>Friends-Only</MenuItem>
              <MenuItem value={3}>Unlisted</MenuItem>
            </Select>
          </StyledFormControl>
        </div>
        <div className={styles.buttonGroup}>
          <Button
            variant="contained"
            size="small"
            onClick={onRequestClose}
            className={styles.cancelButton}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSave}
            className={styles.saveButton}
          >
            Save
          </Button>
        </div>
      </form>
    </Modal>
  );
}

const PostTextField = styled(TextField)({
  "& label": {
    color: "#ffffff !important",
  },

  "& input": {
    color: "white !important",
  },

  "& textarea": {
    color: "white !important",
  },

  "& .MuiOutlinedInput-root": {
    "& fieldset": {
      border: "none",
      boxShadow: "0 4px 7px rgba(0, 0, 0, 0.45)",
    },
    "&:hover fieldset": {
      border: "1px solid",
      borderColor: "white !important",
    },
    "&.Mui-focused fieldset": {
      border: "1px solid",
      borderColor: "#70ffaf !important",
    },
  },

  "& .MuiFormHelperText-root": {
    color: "#ffffff",
    "&.Mui-error": {
      color: "#dc3545",
    },
  },
});
