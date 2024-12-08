import { Box, Button, IconButton, TextField, Tooltip } from "@mui/material";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import { useEffect, useState } from "react";
import EditIcon from '@mui/icons-material/Edit';
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Modal from "react-modal";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";
import styled from "@mui/material/styles/styled";
import styles from "./EditPostModal.module.scss";

interface EditPostModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  post: {
    title: string;
    content: string;
    visibility: any;
    contentType: string;
    description: string;
  } | null; // Allow post to be null or undefined
  onSubmit: (updatedPost: {
    title: string;
    content: string;
    visibility: any;
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
  const [visibility, setVisibility] = useState(post.visibility);
  const [contentType, setContentType] = useState(`${post.contentType}`);
  const [disabled, setDisabled] = useState(true);
  const [isHovered, setIsHovered] = useState(false);

  // Ensure that modal fields reset when `post` data changes
  useEffect(() => {
    if (isOpen && post) {
      // Check if post is defined
      setTitle(post.title);
      setContent(post.content);
      setVisibility(post.visibility);
    }
  }, [isOpen, post]);

  // Disable save button if there are no edits made
  useEffect(() => {
    if (
      title === post.title &&
      content === post.content &&
      normalizeVisibility(visibility) === normalizeVisibility(post.visibility)
    ) {
      setDisabled(true);
    } else {
      setDisabled(false);
    }
  }, [title, content, visibility, post]);

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

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && (file.type === "image/png" || file.type === "image/jpeg")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === "string") {
          setContent(reader.result.split(",")[1]); // base64 string
          file.type === "image/png" ? setContentType("image/png;base64") :
          file.type === "image/jpeg" ? setContentType("image/jpeg;base64") :
            setContentType("application/base64");
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileSelect = () => {
    const fileInput = document.getElementById("image-upload-input");
    fileInput?.click();
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
              <Box
                sx={{
                  position: "relative",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  width: "100%",
                  height: "auto"
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
              >
                <img
                  src={`data:${contentType};base64,${content}`}
                  alt="Uploaded"
                  style={{
                    maxWidth: "40%",
                    height: "40%",
                    opacity: isHovered ? 0.7 : 1,
                    transition: "opacity 0.3s ease",
                    borderRadius: "8px",
                  }}
                />
                {isHovered && (
                  <Tooltip title="Edit Image">
                    <IconButton
                      sx={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        color: "#3f51b5",
                        backgroundColor: "rgba(255, 255, 255, 0.8)",
                        "&:hover": {
                          backgroundColor: "rgba(255, 255, 255, 1)",
                        },
                      }}
                      onClick={triggerFileSelect}
                    >
                      <EditIcon sx={{ fontSize: 30 }} />
                    </IconButton>
                  </Tooltip>
                )}
                <input
                  id="image-upload-input"
                  type="file"
                  accept="image/png, image/jpeg"
                  onChange={handleImageChange}
                  style={{ display: "none" }}
                />
              </Box>
            </div>
          ) : (
            <PostTextField
              className={styles.content_field}
              value={content}
              multiline
              fullWidth
              onChange={(e) => setContent(e.target.value)}
              sx={{
                "& .MuiOutlinedInput-root": {
                  padding: 0,
                },
                "& .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
                "& textarea": {
                  resize: "none", // Remove resize handle
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
              <MenuItem value={"PUBLIC"}>Public</MenuItem>
              <MenuItem value={"FRIENDS"}>Friends-Only</MenuItem>
              <MenuItem value={"UNLISTED"}>Unlisted</MenuItem>
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
            disabled={disabled}
            onClick={handleSave}
            sx={{
              backgroundColor: "#70ffaf",
              color: "black",
              transition: "0.3s ease-in-out",
            }}
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
      border: "none !important",
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
