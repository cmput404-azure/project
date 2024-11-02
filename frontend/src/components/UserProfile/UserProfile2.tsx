import { Alert, Avatar, Button, CircularProgress, IconButton, Snackbar } from "@mui/material";
import { Author, PostData as Post } from "../../models/models";
import { useEffect, useState } from "react";

import FollowList from "../FollowList/FollowList";
import { FollowerModalTypes } from "../../models/modelTypes";
import { GitHub } from "@mui/icons-material";
import LinkIcon from '@mui/icons-material/Link';
import MiniPostCard from "../MiniPostCard/MiniPostCard";
import PostCard from "../PostCard/PostCard";
import ProfileService from "../../service/profile";
import followService from "../../service/follow";
import styles from "./UserProfile2.module.scss";
import { useAuth } from "../../state";

interface FollowersModal{
   open: boolean;
   type: string;
}

export default function UserProfile2() {
   const [authorData, setAuthorData] = useState<Author | null>(null);
   const [posts, setPosts] = useState<Post[]>([]);
   const [isFollowing, setIsFollowing] = useState<boolean>(false);
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
   }, [auth.user.uuid]);

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

   function getLink(){
      const currentURL = window.location.href;
      navigator.clipboard.writeText(currentURL);
      setOpenSnackbar(true);
   }

   if (!authorData) return <div className="loading"><CircularProgress/></div>;

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
                        <Button variant="contained" color="primary" size="small">
                           {isFollowing ? "Unfollow" : "Follow"}
                        </Button>
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
