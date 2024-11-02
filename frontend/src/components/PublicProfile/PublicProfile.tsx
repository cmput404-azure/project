import { Alert, Avatar, Button, CircularProgress, IconButton, Snackbar } from "@mui/material";
import { Author, PostData as Post } from "../../models/models";
import { useEffect, useState } from "react";
import FollowList from "../FollowList/FollowList";
import { Check, GitHub } from "@mui/icons-material";
import LinkIcon from '@mui/icons-material/Link';
import PostCard from "../PostCard/PostCard";
import ProfileService from "../../service/profile";
import FollowService from "../../service/follow";
import InboxService from "../../service/inbox";
import styles from "./PublicProfile.module.scss";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../state";
import { api } from "../../service/config";

const FollowerModalTypes = {
   follower: "Follower",
   following: "Following",
   friends: "Friends",
};

interface FollowersModal {
   open: boolean;
   type: string;
}

export default function PublicProfile() {
   const [authorData, setAuthorData] = useState<Author | null>(null);
   const [posts, setPosts] = useState<Post[]>([]);
   const [isFollowing, setIsFollowing] = useState<boolean>(false);
   const [followersModal, setfollowersModal] = useState<FollowersModal>({ open: false, type: "follower" });
   const [friendsCount, setFriendsCount] = useState(0);
   const [followersCount, setFollowersCount] = useState(0);
   const [followingCount, setFollowingCount] = useState(0);
   const [openSnackbar, setOpenSnackbar] = useState(false);
   const [isAuthenticated, setIsAuthenticated] = useState(true);
   const navigate = useNavigate();

   // TODO: make the follow button change to unfollow if the user is already following the author, or hidden if the user is the author
   const authProvider = useAuth();

   const { userID } = useParams<{ userID: string }>();

   const fetchProfileData = async () => {
      if (userID) {
         const author = await ProfileService.fetchAuthorData(userID);
         const posts = await ProfileService.fetchAuthorPosts(userID);
         setAuthorData(author);
         setPosts(posts);
      }
   };

   useEffect(() => {
      fetchProfileData();
   }, [userID]);

   useEffect(() => {
      async function fetchCounts() {
         try {
            const friends = await FollowService.getFollowers(userID);
            const followers = await FollowService.getFollowers(userID);
            const following = await FollowService.getFollowing(userID);
            setFriendsCount(friends.length);
            setFollowersCount(followers.length);
            setFollowingCount(following.length);
         } catch (error) {
            console.error("Failed to fetch counts:", error);
         }
      }
      async function checkFollowing(){
         console.log("CHECK FOLLOWING");
         const authUser = await api.get<Author>(`/api/authors/${authProvider.user.uuid}/`);
         let url = `${authUser.data.host}authors/${authProvider.user.uuid}`;
         const encodedUrl = encodeURIComponent(url);
         const is_following = await FollowService.checkFollowing(userID, encodedUrl);
         setIsFollowing(is_following);
      }

      fetchCounts();
      if (authProvider.isAuthenticated === false) {
         console.log("FALSE");
         setIsAuthenticated(false);
      }else{
         checkFollowing();
      }
   }, [userID]);

   

   function getLink() {
      const currentURL = window.location.href;
      navigator.clipboard.writeText(currentURL);
      setOpenSnackbar(true);
   }

   async function handleButtonClick() {
      if (isFollowing) {
         // Displaying unfollow button
         await FollowService.unFollow(userID,authProvider.user);
      }else{
         // Displaying follow button, send follower request
            const userResponse = await api.get<Author>(`/api/authors/${authProvider.user.uuid}/`);
            const userInfo = userResponse.data;
      
            const followRequest = {
               type: "follow",
               summary: `${userInfo.displayName} wants to follow ${authorData.displayName}`,
               actor: {
               type: "author",
               id: `${userInfo.id}`,
               host: `${userInfo.host}`,
               displayName: `${userInfo.displayName}`,
               github: `${userInfo.github}`,
               page: `${userInfo.page}`,
               },
            };
      
            await InboxService.sendPostToInbox(userID, followRequest);
      }
   }

   function handleLoginClick(){
      navigate('/login');
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
                        <Button
                           variant="contained"
                           color="primary"
                           size="small"
                           onClick={isAuthenticated ? handleButtonClick : handleLoginClick}
                        >
                           {isAuthenticated ? (isFollowing ? "Unfollow" : "Follow") : "Login"}
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
                           <p className={styles.followers__count} onClick={() => setfollowersModal({ open: true, type: FollowerModalTypes.follower })}>
                              <b>{followersCount}</b> {followersCount === 1 ? "follower" : "followers"}
                           </p>
                           <p className={styles.following__count} onClick={() => setfollowersModal({ open: true, type: FollowerModalTypes.following })}>
                              <b>{followingCount}</b> following
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
                  <PostCard key={post.id} post={post} />
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
