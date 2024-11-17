import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Button,
} from "@mui/material";

import follow from "../../service/follow";
import { PostData } from "../../models/models";
import profileService from "../../service/profile";
import share from "../../service/share";
import { useAuth } from "../../state";
import inbox from "../../service/inbox";
import { Share } from "../../models/models";

interface ShareDialogueProps {
  post: PostData;
  isDialogOpen: boolean;
  setHasShared: React.Dispatch<React.SetStateAction<boolean>>;
  onClose: () => void;
}

export default function ShareDialogue({
  post,
  isDialogOpen,
  setHasShared,
  onClose,
}: ShareDialogueProps) {
  // const [shareDialogOpen, setShareDialogOpen] = useState<boolean>(isDialogOpen);
  const authProvider = useAuth();

  // Update shareDialogOpen when isDialogOpen prop changes
  // useEffect(() => {
  //   setShareDialogOpen(isDialogOpen);
  // }, [isDialogOpen]);

  // const handleCloseShare = () => {
  //   setShareDialogOpen(false);
  // };

  // Function to confirm sharing
  const handleConfirmShare = async () => {
    // setShareDialogOpen(false);
    onClose();
    // Get followers and share the post
    const currentUser = await profileService.fetchAuthorData(
      authProvider.user.uuid
    );
    const followers = await follow.getFollowers(authProvider.user.uuid);

    for (const follower of followers) {
      const share_obj = {
        type: "share",
        sharer: authProvider.user.uuid,
        post: post.id,
      };

      await inbox.sendPostToInbox(follower.id, share_obj);
    }

    // Add directly to the share model with receiver as null
    const share_obj: Share = {
      post: post.id,
    };

    await share.addShare(share_obj, authProvider.user.uuid);
    setHasShared(true);
  };

  return (
    <Dialog
      open={isDialogOpen}
      onClose={onClose}
      sx={{
        "& .MuiDialog-paper": {
          backgroundColor: "rgb(123, 123, 123)",
          color: "white",
        },
      }}
    >
      <DialogTitle>Share Post</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ color: "white" }}>
          Do you want to share this post with all your friends and followers?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={onClose}
          sx={{
            backgroundColor: "lightcoral",
            color: "white",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.2)",
            "&:hover": {
              backgroundColor: "#e57373",
            },
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleConfirmShare}
          sx={{
            backgroundColor: "#5acc8c",
            color: "white",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.2)",
            "&:hover": {
              backgroundColor: "#4ba578",
            },
          }}
        >
          Share
        </Button>
      </DialogActions>
    </Dialog>
  );
}
