import * as React from "react";
import { styled, alpha } from "@mui/material/styles";
import Menu, { MenuProps } from "@mui/material/Menu";
import { MenuItem, Divider, IconButton, Alert, Snackbar } from "@mui/material";
import { MoreVert, Link, Edit, Delete } from "@mui/icons-material";
import { useState } from "react";
import { PostData } from "../../models/models";
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import follow from "../../service/follow";
import inbox from "../../service/inbox";
import EditPostModal from "../EditPostModal/EditPostModal";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";

const StyledMenu = styled((props: MenuProps) => (
  <Menu
    elevation={0}
    anchorOrigin={{
      vertical: "bottom",
      horizontal: "right",
    }}
    transformOrigin={{
      vertical: "top",
      horizontal: "right",
    }}
    {...props}
  />
))(({ theme }) => ({
  "& .MuiPaper-root": {
    borderRadius: 6,
    marginTop: theme.spacing(1),
    minWidth: 180,
    color: "rgb(55, 65, 81)",
    boxShadow:
      "rgb(255, 255, 255) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 0px 0px 1px, rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.05) 0px 4px 6px -2px",
    "& .MuiMenu-list": {
      padding: "4px 0",
    },
    "& .MuiMenuItem-root": {
      "& .MuiSvgIcon-root": {
        fontSize: 18,
        color: theme.palette.text.secondary,
        marginRight: theme.spacing(1.5),
      },
      "&:active": {
        backgroundColor: alpha(
          theme.palette.primary.main,
          theme.palette.action.selectedOpacity
        ),
      },
    },
    ...theme.applyStyles("dark", {
      color: theme.palette.grey[300],
    }),
  },
}));

interface EllipseMenuProps {
  post: PostData;
  authorUUID: string;
  onDelete?: (postId: string) => void;
}

// inspired from https://mui.com/material-ui/react-menu/#customization, Downloaded on 2024-11-16
export default function EllipseMenu({
  post,
  authorUUID,
  onDelete,
}: EllipseMenuProps) {
  const [editModal, setEditModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [postData, setPostData] = useState<PostData>(post);
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const openEditModal = () => setEditModal(true);
  const closeEditModal = () => setEditModal(false);
  const openDeleteModal = () => setDeleteModal(true);
  const closeDeleteModal = () => setDeleteModal(false);

  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    openEditModal();
    handleClose();
  };

  const handleDelete = () => {
    openDeleteModal();
    handleClose();
  };

  const handleCopyLink = () => {
    if (post) {
      const domain = window.location.host;
      const path = `/#/post/${encodeURIComponent(post.id)}`;

      const link = `${domain}${path}`;
      navigator.clipboard.writeText(link).then(
        () => setOpenSnackbar(true),
        (err) => console.error("Could not copy link: ", err)
      );
    }
  };

  const handleCloseSnackbar = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason !== "clickaway") setOpenSnackbar(false);
  };

  async function handleUpdatePost(updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) {
    try {
      const postId = extractUUID(postData.id);
      await api.put(
        `/api/authors/${extractUUID(authorUUID)}/posts/${postId}/`,
        updatedPost
      ); // Model will auto convert integer to string

      const followers = await follow.getFollowers(extractUUID(authorUUID));
      const friends = await follow.getFriends(extractUUID(authorUUID));
      const target =
        normalizeVisibility(postData.visibility) === 1 ||
        normalizeVisibility(postData.visibility) === 3
          ? followers
          : friends;
      for (const recipient of target) {
        const post_obj = {
          ...postData,
          ...(postData.type ? {} : { type: "post" }),
          title: updatedPost.title,
          content: updatedPost.content,
          visibility: updatedPost.visibility,
          follower: {
            type: "author",
            id: recipient.id,
            host: recipient.host,
          },
        };
        
        await inbox.updateInboxPost(recipient.id, post_obj);
      }

      // Update local postData state
      setPostData({
        ...postData,
        title: updatedPost.title,
        content: updatedPost.content,
        visibility: normalizeVisibility(updatedPost.visibility, true) as string,
      });

      window.location.reload();
      closeEditModal();
    } catch (error) {
      console.error("Error updating post", error);
    }
  }

  async function handleDeletePost() {
    try {
      const postId = extractUUID(postData.id);
      await api.delete(
        `/api/authors/${extractUUID(authorUUID)}/posts/${postId}/`
      );

      const followers = await follow.getFollowers(extractUUID(authorUUID));
      const friends = await follow.getFriends(extractUUID(authorUUID));
      const target =
        normalizeVisibility(postData.visibility) === 1 ||
        normalizeVisibility(postData.visibility) === 3
          ? followers
          : friends;
      for (const recipient of target) {
        const deletedPost = {
          ...postData,
          ...(postData.type ? {} : { type: "post" }),
          follower: {
            type: "author",
            id: recipient.id,
            host: recipient.host,
          },
        };
        await inbox.deleteInboxPost(recipient.id, deletedPost);
      }

      // Update postData state to indicate deletion
      setPostData({ ...postData, visibility: "DELETED" });
      closeDeleteModal();
      onDelete(postData.id);
    } catch (error) {
      console.error("Error deleting post", error);
    }
  }

  return (
    <div>
      <IconButton
        aria-label="more"
        id="long-button"
        aria-controls={open ? "long-menu" : undefined}
        aria-expanded={open ? "true" : undefined}
        aria-haspopup="true"
        onClick={handleClick}
        sx={{ color: "white" }}
      >
        <MoreVert />
      </IconButton>
      <StyledMenu
        id="demo-customized-menu"
        MenuListProps={{
          "aria-labelledby": "demo-customized-button",
        }}
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
      >
        <MenuItem onClick={handleCopyLink} disableRipple>
          <Link />
          Get Link
        </MenuItem>

        <Snackbar
          open={openSnackbar}
          autoHideDuration={2000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity="success"
            sx={{ width: "100%" }}
          >
            Link copied to clipboard!
          </Alert>
        </Snackbar>

        <MenuItem onClick={handleEdit} disableRipple>
          <Edit />
          Edit
        </MenuItem>
        <Divider sx={{ my: 0.5 }} />
        <MenuItem onClick={handleDelete} disableRipple>
          <Delete />
          Delete
        </MenuItem>
      </StyledMenu>

      <EditPostModal
        isOpen={editModal}
        onRequestClose={closeEditModal}
        post={postData}
        onSubmit={handleUpdatePost}
      />

      <DeletePostModal
        isOpen={deleteModal}
        onRequestClose={closeDeleteModal}
        onDelete={handleDeletePost}
      />
    </div>
  );
}
