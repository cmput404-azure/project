import { Author, Post } from "../../models/models";
import { Avatar, Button, Icon, IconButton } from "@mui/material";
import { useEffect, useState } from "react";

import FollowList from "../FollowList/FollowList";
import { GitHub } from "@mui/icons-material";
import LinkIcon from '@mui/icons-material/Link';
import PostCard from "../PostCard/PostCard";
import ProfileService from "../../service/profile";
import followService from "../../service/follow";
import styles from "./PublicProfile.module.scss";
import { useParams } from "react-router-dom";

export default function PublicProfile() {
   const [authorData, setAuthorData] = useState<Author | null>(null);
   const [posts, setPosts] = useState<Post[]>([]);
   const [isFollowing, setIsFollowing] = useState<boolean>(false);
   const [friendsCount, setFriendsCount] = useState(0);
   const [followersCount, setFollowersCount] = useState(0);
   const [followingCount, setFollowingCount] = useState(0);


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
            const friends = await followService.getFollowers(userID);
            const followers = await followService.getFollowers(userID);
            const following = await followService.getFollowing(userID);

            setFriendsCount(friends.length);
            setFollowersCount(followers.length);
            setFollowingCount(following.length);
         } catch (error) {
            console.error("Failed to fetch counts:", error);
         }
      }

      fetchCounts();
   }, [userID]);

   if (!authorData) return <div>Loading...</div>;

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
                           <IconButton onClick={() => window.open(authorData.github, "_blank")}>
                              <GitHub />
                           </IconButton>
                        }
                     </div>
                     <div className={styles.user__secondary}>
                        <p className={styles.username}>@{authorData.username}</p>

                        <div className={styles.follows}>
                           <p className={styles.posts__count}>
                              <b>{posts.length}</b> {posts.length === 1 ? "post" : "posts"}
                           </p>
                           <p className={styles.followers__count}>
                              <b>{followersCount}</b> {followersCount === 1 ? "follower" : "followers"}
                           </p>
                           <p className={styles.following__count}>
                              <b>{followingCount}</b> following
                           </p>
                           <p className={styles.friends__count}>
                              <b>{friendsCount}</b> {friendsCount === 1 ? "friend" : "friends"}
                           </p>
                        </div>
                     </div>
                  </div>
                  <div className={styles.footer}>
                     <IconButton>
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
      </div>
   );
}
