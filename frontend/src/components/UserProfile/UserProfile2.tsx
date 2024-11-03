import { Alert, Avatar, Box, Button, CircularProgress, Drawer, IconButton, Snackbar, TextField } from "@mui/material";
import { Author, PostData as Post, User } from "../../models/models";
import { Edit, GitHub } from "@mui/icons-material";
import { useEffect, useState } from "react";

import CloseIcon from '@mui/icons-material/Close';
import EditIcon from '@mui/icons-material/Edit';
import FollowList from "../FollowList/FollowList";
import { FollowerModalTypes } from "../../models/modelTypes";
import LinkIcon from '@mui/icons-material/Link';
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import ProfileService from "../../service/profile";
import { extractUUID } from "../../util/formatting/extractUUID";
import followService from "../../service/follow";
import profileService from "../../service/profile";
import styles from "./UserProfile2.module.scss";
import { useAuth } from "../../state";

interface FollowersModal {
   open: boolean;
   type: string;
}

export default function UserProfile2() {
   const [authorData, setAuthorData] = useState<Author | null>(null);
   const [posts, setPosts] = useState<Post[]>([]);
   const [edit, setEdit] = useState<boolean>(false);
   const [followersModal, setfollowersModal] = useState<FollowersModal>({ open: false, type: "follower" });
   const [friendsCount, setFriendsCount] = useState(0);
   const [followersCount, setFollowersCount] = useState(0);
   const [followingCount, setFollowingCount] = useState(0);
   const [openSnackbar, setOpenSnackbar] = useState(false);
   const auth = useAuth();

   const fetchProfileData = async () => {
      if (auth.isAuthenticated && auth.user.uuid) {
         const author = await ProfileService.fetchAuthorData(auth.user.uuid);
         const posts = await ProfileService.fetchAuthorPosts(auth.user.uuid);
         setAuthorData(author);
         setPosts(posts);
      }
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
            const friends = await followService.getFollowers(auth.user.uuid);
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
      const currentURL = window.location.href;
      navigator.clipboard.writeText(currentURL);
      setOpenSnackbar(true);
   }

   if (!authorData) return <div className="loading"><CircularProgress /></div>;

   return (
      <div className={styles.wrapper}>
         <div className={styles.container}>
            <section className={styles.header}>
               <div className={styles.info}>
                  <div className={styles.icon}>
                     <Avatar
                        alt={authorData.displayName}
                        src={authorData.profileImage ?? "https://ui-avatars.com/api/?name=" + authorData.displayName}
                        sx={{ width: 100, height: 100 }}
                     />
                  </div>
                  <div className={styles.user}>
                     <div className={styles.user__main}>
                        <h2 className={styles.display__name}>{authorData.displayName}</h2>
                        <IconButton className={styles.icon__button} size="small" onClick={() => setEdit(true)}>
                           <EditIcon />
                        </IconButton>
                        {authorData.github &&
                           <IconButton className={styles.icon__button}
                              size="small"
                              onClick={() => window.open(authorData.github, "_blank")}>
                              <GitHub />
                           </IconButton>
                        }
                     </div>
                     <div className={styles.user__secondary}>
                        <p className={styles.username}>@{authorData.username}</p>

                        <div className={styles.follows}>
                           <p className={styles.posts__count} >
                              <b>{posts.length}</b> {posts.length === 1 ? "post" : "posts"}
                           </p>
                           <p className={styles.followers__count} onClick={() => setfollowersModal({ open: true, type: FollowerModalTypes.FOLLOWER })}>
                              <b>{followersCount}</b> {followersCount === 1 ? "follower" : "followers"}
                           </p>
                           <p className={styles.following__count} onClick={() => setfollowersModal({ open: true, type: FollowerModalTypes.FOLLOWING })}>
                              <b>{followingCount}</b> following
                           </p>
                           <p className={styles.friends__count} onClick={() => setfollowersModal({ open: true, type: FollowerModalTypes.FRIENDS })}>
                              <b>{friendsCount}</b> {friendsCount === 1 ? "friend" : "friends"}
                           </p>
                           <FollowList
                              isOpen={followersModal.open}
                              onClose={() => setfollowersModal({ open: false, type: "follower" })}
                              isFollowerList={followersModal.type}
                           />
                        </div>
                     </div>
                  </div>
                  <div className={styles.footer}>
                     <IconButton className={styles.icon__button} size="small" onClick={getLink}>
                        <LinkIcon />
                     </IconButton>
                  </div>
               </div>
               <div className={styles.bio}>
                  <p className={styles.bio__text}>{authorData.bio}</p>
               </div>
            </section>

            <section className={styles.posts}>
               {posts.map(post => (
                  <MiniPostCard key={post.id} post={post} authorUUID={authorData.id} onDelete={onDeletePost} />
               ))}
            </section>
         </div>

         <Drawer open={edit} anchor="right" onClose={() => setEdit(false)}
            PaperProps={{
               sx: { bgcolor: "#555", color: "#fff" }
            }}
         >
            <EditProfile user={authorData} toggleDrawer={setEdit} />
         </Drawer>

         <Snackbar
            open={openSnackbar}
            autoHideDuration={2000} // auto close after 2s
            onClose={() => setOpenSnackbar(false)}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
         >
            <Alert onClose={() => setOpenSnackbar(false)} severity="success" sx={{ width: '100%' }}>
               Link copied to clipboard!
            </Alert>
         </Snackbar>
      </div>
   );
}

export function EditProfile({ user, toggleDrawer }: { user: Author, toggleDrawer: (value: boolean) => void }) {
   const [displayName, setDisplayName] = useState<string>(user.displayName);
   const [bio, setBio] = useState<string>(user.bio ?? "");
   const [github, setGithub] = useState<string>(user.github ?? "");
   const [profileImage, setProfileImage] = useState<string>(user.profileImage ?? "");
   const [profileImageFile, setProfileImageFile] = useState<File | null>(null);
   const [loading, setLoading] = useState<boolean>(false);
   const [error, setError] = useState<string>("");
   const [success, setSuccess] = useState<boolean>(false);
   const [disabled, setDisabled] = useState<boolean>(false);

   user.id = extractUUID(user.id);

   function convertToBase64(file: File): Promise<string> {
      return new Promise((resolve, reject) => {
         const reader = new FileReader();
         reader.readAsDataURL(file);
         reader.onload = () => resolve(reader.result as string);
         reader.onerror = error => reject(error);
      });
   }

   async function handleUpdate() {
      setError("");

      // Validation
      if (!displayName) {
         setError("Display name is required");
         return;
      }

      if (!github) {
         setError("Github is required");
         return;
      }

      // Create new user object
      const updatedUser: Author = {
         ...user,
         displayName,
         bio,
         github,
         profileImage: URL.createObjectURL(profileImageFile ?? new Blob())
      };

      setLoading(true);

      try {
         // Check if a new profile image file exists
         if (profileImageFile) {
            const image = await convertToBase64(profileImageFile);
            updatedUser.profileImage = image;
         }

         await profileService.updateUserInfo(user.id, updatedUser);

         setSuccess(true);
         setLoading(false);
         setDisabled(true);
      }
      catch (error: any) {
         setError(error.message);
         setLoading(false);
      }
   }

   // Check disabled if no changes
   useEffect(() => {
      if (displayName === user.displayName && bio === user.bio && github === user.github && profileImage === user.profileImage) {
         setDisabled(true);
      } else {
         setDisabled(false);
      }
   }, [displayName, bio, github, profileImage]);


   return (
      <div className={styles.edit__profile}>
         <div className={styles.edit__profile__header}>
            <h2>Edit Profile</h2>
            <IconButton className={styles.icon__button} size="small" onClick={() => toggleDrawer(false)}>
               <CloseIcon />
            </IconButton>
         </div>

         <div className={styles.edit__profile__body}>
            <div className={styles.edit__profile__body__image}>
               <div className={styles.edit__profile__body__image__container}>
                  <Avatar alt="profile image" src={profileImage} sx={{ width: 100, height: 100 }} />
               </div>
               <div className={styles.edit__profile__body__image__input}>
                  <input type="file" accept="image/*" onChange={e => {
                     if (e.target.files) {
                        setProfileImageFile(e.target.files[0]);
                        setProfileImage(URL.createObjectURL(e.target.files[0]));
                     }
                  }} />
               </div>
            </div>

            <div className={styles.edit__profile__body__form}>
               <TextField className={styles.input} label="Display Name" variant="outlined" value={displayName} onChange={e => setDisplayName(e.target.value)} />
               <TextField className={styles.input} label="Bio" variant="outlined" value={bio} onChange={e => setBio(e.target.value)} />
               <TextField className={styles.input} label="Github" variant="outlined" value={github} onChange={e => setGithub(e.target.value)} />
            </div>
         </div>

         <p className={styles.error}>{error}</p>

         <Button variant="contained" onClick={handleUpdate} disabled={disabled} sx={{ width: "100%", marginTop: "1rem" }}>
            {loading ? <CircularProgress /> : "Save"}
         </Button>
         <Snackbar
            open={success}
            autoHideDuration={2000}
            onClose={() => setSuccess(false)}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
         >
            <Alert onClose={() => setSuccess(false)} severity="success" sx={{ width: '100%' }}>
               Successfully updated profile.
            </Alert>
         </Snackbar>   
      </div>
   );
}