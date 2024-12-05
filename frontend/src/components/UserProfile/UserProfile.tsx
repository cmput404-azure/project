import {
   Alert,
   Avatar,
   Box,
   Button,
   CircularProgress,
   Drawer,
   IconButton,
   Snackbar,
   TextField,
   styled,
} from "@mui/material";
import { Author, PostData } from "../../models/models";
import { CloudUpload, GitHub } from "@mui/icons-material";
import { useEffect, useRef, useState } from "react";

import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import FollowList from "../FollowList/FollowList";
import { FollowerModalTypes } from "../../models/modelTypes";
import LinkIcon from "@mui/icons-material/Link";
import Post from "../Post/Post";
import ProfileService from "../../service/profile";
import Tooltip from "@mui/material/Tooltip";
import { extractUUID } from "../../util/formatting/extractUUID";
import followService from "../../service/follow";
import profileService from "../../service/profile";
import styles from "./UserProfile.module.scss";
import { useAuth } from "../../state";

interface FollowersModal {
   open: boolean;
   type: string;
}

export default function UserProfile() {
   const [authorData, setAuthorData] = useState<Author | null>(null);
   const [posts, setPosts] = useState<PostData[]>([]);
   const [edit, setEdit] = useState<boolean>(false);
   const [followersModal, setfollowersModal] = useState<FollowersModal>({
      open: false,
      type: "follower",
   });
   const [friendsCount, setFriendsCount] = useState(0);
   const [followersCount, setFollowersCount] = useState(0);
   const [followingCount, setFollowingCount] = useState(0);
   const [openSnackbar, setOpenSnackbar] = useState(false);
   const [page, setPage] = useState(1);
   const [totalPages, setTotalPages] = useState(0);
   const [loading, setLoading] = useState(false);
   const [postCount, setPostCount] = useState(0);
   const pageSize = 10;

   const auth = useAuth();

   const fetchProfileData = async () => {
      if (auth.isAuthenticated && auth.user.uuid) {
         const author = await ProfileService.fetchAuthorData(auth.user.uuid);
         setAuthorData(author);

         await fetchPosts(auth.user.uuid);
      }
   };

   const fetchPosts = async (userId: string, page: number = 1) => {
      if (loading) return;
      setLoading(true);
      const { count, src } = await ProfileService.fetchAuthorPosts(userId, page);
      setPostCount(count);

      setPosts((prevPosts) => {
         const existingIds = new Set(prevPosts.map((post) => post.id));
         const newPosts = src.filter((post) => !existingIds.has(post.id));
         return [...prevPosts, ...newPosts];
      });

      setTotalPages(Math.ceil(count / pageSize));
      setLoading(false);
   };

   const nextPage = async () => {
      if (loading || page >= totalPages) return;
      await fetchPosts(auth.user.uuid, page + 1);
      setPage((prevPage) => prevPage + 1);
   };

   function onDeletePost(postId: string) {
      setPosts(posts.filter((post) => post.id !== postId));
   }

   useEffect(() => {
      fetchProfileData();
   }, [auth.user.uuid, edit]);

   useEffect(() => {
      async function fetchCounts() {
         try {
            const friends = await followService.getFriends(auth.user.uuid);
            const followers = await followService.getFollowers(auth.user.uuid);
            const following = await followService.getFollowing(auth.user.uuid);

            setFriendsCount(friends.length);
            setFollowersCount(followers.length);
            setFollowingCount(following.length);
         } catch (error) {
            console.error("Failed to fetch counts:", error);
         }
      }

      fetchCounts();
   }, [auth.user.uuid]);

   function getLink() {
      const currentURL = window.location.host;
      const protocol = window.location.protocol;
      const constructedURL = `${protocol}//${currentURL}/#/authors/${extractUUID(
         auth.user.uuid
      )}`;

      navigator.clipboard.writeText(constructedURL);
      setOpenSnackbar(true);
   }

   if (!authorData)
      return (
         <div className="loading">
            <CircularProgress sx={{ color: "#70ffaf" }} />
         </div>
      );

   return (
      <div className={styles.wrapper}>
         <div className={styles.container}>
            <section className={styles.header}>
               <div className={styles.info}>
                  <div className={styles.icon}>
                     <Avatar
                        alt={authorData.displayName}
                        src={
                           profileService.getProfilePicture(authorData)
                        }
                        sx={{ width: 100, height: 100 }}
                     />
                  </div>
                  <div className={styles.user}>
                     <div className={styles.user__main}>
                        <h2 className={styles.display__name}>
                           {authorData.displayName}
                        </h2>
                        <IconButton
                           className={styles.icon__button}
                           size="small"
                           onClick={() => setEdit(true)}
                        >
                           <EditIcon />
                        </IconButton>
                        {authorData.github && (
                           <IconButton
                              className={styles.icon__button}
                              size="small"
                              onClick={() => window.open(authorData.github, "_blank")}
                           >
                              <GitHub />
                           </IconButton>
                        )}
                     </div>
                     <div className={styles.user__secondary}>
                        <p className={styles.username}>@{authorData.username}</p>

                        <div className={styles.follows}>
                           <p className={styles.posts__count}>
                              <b>{postCount}</b> {postCount === 1 ? "post" : "posts"}
                           </p>
                           <p
                              className={styles.followers__count}
                              onClick={() =>
                                 setfollowersModal({
                                    open: true,
                                    type: FollowerModalTypes.FOLLOWER,
                                 })
                              }
                           >
                              <b>{followersCount}</b>{" "}
                              {followersCount === 1 ? "follower" : "followers"}
                           </p>
                           <p
                              className={styles.following__count}
                              onClick={() =>
                                 setfollowersModal({
                                    open: true,
                                    type: FollowerModalTypes.FOLLOWING,
                                 })
                              }
                           >
                              <b>{followingCount}</b> following
                           </p>
                           <p
                              className={styles.friends__count}
                              onClick={() =>
                                 setfollowersModal({
                                    open: true,
                                    type: FollowerModalTypes.FRIENDS,
                                 })
                              }
                           >
                              <b>{friendsCount}</b>{" "}
                              {friendsCount === 1 ? "friend" : "friends"}
                           </p>
                           <FollowList
                              isOpen={followersModal.open}
                              onClose={() =>
                                 setfollowersModal({ open: false, type: "follower" })
                              }
                              isFollowerList={followersModal.type}
                           />
                        </div>
                     </div>
                  </div>
                  <div className={styles.footer}>
                     <IconButton
                        className={styles.icon__button}
                        size="small"
                        onClick={getLink}
                     >
                        <LinkIcon />
                     </IconButton>
                  </div>
               </div>
               <div className={styles.bio}>
                  <p className={styles.bio__text}>{authorData.bio}</p>
               </div>
            </section>

            <section className={styles.posts}>
               {!loading ? posts.length > 0 ? posts.map((post) => (
                  <Post
                     key={post.id}
                     postGiven={post}
                     canToggleComments={false}
                     disableLikeComment={true}
                     onDeletePost={onDeletePost}
                  />
               )) : (
                  <div className={"loading_component"}>
                     <p>You have no posts yet 😑</p>
                  </div>
               ) : (
                  <div className={"loading_component"}>
                     <CircularProgress size={24} sx={{ color: "#70ffaf" }} />
                  </div>
               )}
               {page < totalPages && (
                  <Button
                     variant="contained"
                     onClick={nextPage}
                     disabled={loading}
                     sx={{
                        marginTop: "1rem",
                        backgroundColor: "#70ffaf",
                        color: "black",
                     }}
                  >
                     {loading ? (
                        <CircularProgress size={24} sx={{ color: "#70ffaf" }} />
                     ) : (
                        "Load More"
                     )}
                  </Button>
               )}
            </section>
         </div>

         <Drawer
            open={edit}
            anchor="right"
            onClose={() => setEdit(false)}
            PaperProps={{
               sx: { bgcolor: "#555", color: "#fff" },
            }}
         >
            <EditProfile user={authorData} toggleDrawer={setEdit} />
         </Drawer>

         <Snackbar
            open={openSnackbar}
            autoHideDuration={2000} // auto close after 2s
            onClose={() => setOpenSnackbar(false)}
            anchorOrigin={{ vertical: "top", horizontal: "right" }}
         >
            <Alert
               onClose={() => setOpenSnackbar(false)}
               severity="success"
               sx={{ width: "100%" }}
            >
               Link copied to clipboard!
            </Alert>
         </Snackbar>
      </div>
   );
}

export function EditProfile({
   user,
   toggleDrawer,
}: {
   user: Author;
   toggleDrawer: (value: boolean) => void;
}) {
   const [displayName, setDisplayName] = useState<string>(user.displayName);
   const [bio, setBio] = useState<string>(user.bio ?? "");
   const [github, setGithub] = useState<string>(user.github ?? "");
   const [profileImage, setProfileImage] = useState<string>(
      user.profileImage ?? null
   );
   const [loading, setLoading] = useState<boolean>(false);
   const [error, setError] = useState<string>("");
   const [success, setSuccess] = useState<boolean>(false);
   const [disabled, setDisabled] = useState<boolean>(false);
   const githubUsername =
      extractUUID(github) === "login" ? "" : extractUUID(github);
   const fileInputRef = useRef<HTMLInputElement | null>(null);
   const [hovered, setHovered] = useState(false);

   const auth = useAuth();

   user.id = extractUUID(user.id);

   async function handleUpdate() {
      setError("");

      // Validation
      if (!displayName) {
         setError("Display name cannot be empty!");
         return;
      }

      if (!github) {
         setError("Github is required");
         return;
      }

      // Create new user object to store updated data
      const updatedUser: Author = {
         ...user,
         displayName,
         bio,
         github,
         profileImage,
      };

      setLoading(true);

      try {
         if (profileImage) {
            updatedUser.profileImage = profileImage; // Saving the dataURL object
         }

         await profileService.updateUserInfo(user.id, updatedUser);

         setSuccess(true);
         setLoading(false);
         setDisabled(true);

         // Set new auth user with updated user data
         auth.initializeAuth();
      } catch (error: any) {
         setError(error.message);
         setLoading(false);
      }
   }

   // Check disabled if no changes
   useEffect(() => {
      if (
         displayName === user.displayName &&
         bio === user.bio &&
         github === user.github &&
         profileImage === user.profileImage
      ) {
         setDisabled(true);
      } else {
         setDisabled(false);
      }
   }, [displayName, bio, github, profileImage]);

   const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
         const reader = new FileReader();
         reader.onloadend = () => {
            const dataURL = reader.result?.toString() || "";
            setProfileImage(dataURL);
            setHovered(false);
         };
         reader.readAsDataURL(file); // get the dataURL
      }
   };

   const handleGithubChange = (value: string) => {
      if (value.trim() === "") {
         setGithub("https://github.com/login");
      } else {
         setGithub(`https://github.com/${value}`);
      }
   };

   const handleUploadButtonClick = () => {
      fileInputRef?.current.click();
   };

   const handleDeleteImage = () => {
      setProfileImage(null);
      setHovered(false);
   };

   return (
      <div className={styles.edit__profile}>
         <div className={styles.edit__profile__header}>
            <h2>     Edit Profile    </h2>
            <IconButton
               className={styles.icon__button}
               size="small"
               onClick={() => toggleDrawer(false)}
            >
               <CloseIcon />
            </IconButton>
         </div>

         <div className={styles.edit__profile__body}>
            <div className={styles.edit__profile__body__image}>
               <div className={styles.edit__profile__body__image__container}>
                  <Box
                     sx={{
                        position: "relative",
                        width: 100,
                        height: 100,
                        display: "inline-block",
                     }}
                     onMouseEnter={() => profileImage && setHovered(true)}
                     onMouseLeave={() => profileImage && setHovered(false)}
                  >
                     <Avatar
                        alt="profile image"
                        src={profileImage === null ? profileService.getProfilePicture(user, true) : profileImage}
                        sx={{
                           width: 100,
                           height: 100,
                           opacity: hovered ? 0.7 : 1,
                           transition: "opacity 0.3s ease",
                        }}
                     />

                     {hovered && profileImage && (
                        <Tooltip title="Delete Profile Picture">
                           <IconButton
                              sx={{
                                 position: "absolute",
                                 top: "50%",
                                 left: "50%",
                                 transform: "translate(-50%, -50%)",
                                 color: "#ff1744",
                                 backgroundColor: "rgba(255, 255, 255, 0.8)",
                                 "&:hover": {
                                    backgroundColor: "rgba(255, 255, 255, 1)",
                                 },
                              }}
                              onClick={handleDeleteImage}
                           >
                              <DeleteIcon />
                           </IconButton>
                        </Tooltip>
                     )}
                  </Box>
               </div>
               <div className={styles.edit__profile__body__image__input}>
                  <input
                     id="upload-button"
                     type="file"
                     accept="image/*"
                     onChange={handleFileUpload}
                     hidden
                     ref={fileInputRef}
                  />
                  <label htmlFor="upload-button">
                     <Button
                        variant="outlined"
                        size="small"
                        color="secondary"
                        startIcon={<CloudUpload />}
                        onClick={handleUploadButtonClick}
                        sx={{
                           color: "#70ffaf",
                           borderColor: "#70ffaf",
                           "&:hover": {
                              backgroundColor: "#70ffaf",
                              color: "#ffffff",
                           },
                        }}
                     >
                        Upload Image
                     </Button>
                  </label>
               </div>
            </div>

            <div className={styles.edit__profile__body__form}>
               <EditField
                  className={styles.input}
                  label="Display Name"
                  variant="outlined"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
               />
               <EditField
                  className={styles.input}
                  label="Bio"
                  variant="outlined"
                  placeholder="Enter a personal bio"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
               />
               <EditField
                  className={styles.input}
                  label="Github Username"
                  placeholder="Enter your github username"
                  variant="outlined"
                  value={githubUsername}
                  onChange={(e) => handleGithubChange(e.target.value)}
               />
            </div>
         </div>

         <p className={styles.error}>{error}</p>

         <Button
            variant="contained"
            onClick={handleUpdate}
            disabled={disabled}
            sx={{
               width: "100%",
               marginTop: "1rem",
               backgroundColor: "#70ffaf",
               color: "black",
            }}
         >
            {loading ? <CircularProgress sx={{ color: "#70ffaf" }} /> : "Save"}
         </Button>
         <Snackbar
            open={success}
            autoHideDuration={2000}
            onClose={() => setSuccess(false)}
            anchorOrigin={{ vertical: "top", horizontal: "right" }}
         >
            <Alert
               onClose={() => setSuccess(false)}
               severity="success"
               sx={{ width: "100%" }}
            >
               Successfully updated profile.
            </Alert>
         </Snackbar>
      </div>
   );
}

const EditField = styled(TextField)({
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
