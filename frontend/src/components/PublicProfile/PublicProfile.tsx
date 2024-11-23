import {
  Alert,
  Avatar,
  Button,
  CircularProgress,
  IconButton,
  Snackbar,
} from "@mui/material";
import { Author, PostData as PostModel } from "../../models/models";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import FollowList from "../FollowList/FollowList";
import FollowService from "../../service/follow";
import { GitHub } from "@mui/icons-material";
import InboxService from "../../service/inbox";
import LinkIcon from "@mui/icons-material/Link";
import Post from "../Post/Post";
import PostCard from "../PostCard/PostCard";
import ProfileService from "../../service/profile";
import { extractHost } from "../../util/formatting/extractHost";
import profileService from "../../service/profile";
import styles from "./PublicProfile.module.scss";
import { useAuth } from "../../state";

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
  const [posts, setPosts] = useState<PostModel[]>([]);
  const [isFollowing, setIsFollowing] = useState<boolean>(false);
  const [followersModal, setfollowersModal] = useState<FollowersModal>({
    open: false,
    type: "Follower",
  });
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [isRequested, setIsRequested] = useState(false);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [postCount, setPostCount] = useState(0);
  const pageSize = 10;
  const navigate = useNavigate();

  const authProvider = useAuth();
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  const { userID } = useParams<{ userID: string }>();

  useEffect(() => {
    fetchProfileData();
  }, [userID]);

  const fetchProfileData = async () => {
    if (userID) {
      setPosts([]); // clear previous posts, this ensures that when going from one public profile to another, hte previous posts are not shown
      const author = await ProfileService.fetchAuthorData(userID);
      setAuthorData(author);
      setPage(1);
      await fetchPosts(userID);
    }
  };

  const fetchPosts = async (userId: string, page: number = 1) => {
    if (loading) return;
    setLoading(true);
    const { count, src } = await ProfileService.fetchAuthorPosts(userId, page);
    setPostCount(count); // if filter is done properly, count should represent the number of public posts

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
    await fetchPosts(userID, page + 1);
    setPage((prevPage) => prevPage + 1);
  };

  useEffect(() => {
    // Wait for authProvider to initialize
    if (authProvider.isAuthenticated === undefined) {
      setIsAuthLoading(true);
      return;
    }

    setIsAuthLoading(false);

    async function fetchCounts() {
      try {
        const followers = await FollowService.getFollowers(userID);
        const following = await FollowService.getFollowing(userID);
        setFollowersCount(followers.length);
        setFollowingCount(following.length);
      } catch (error) {
        console.error("Failed to fetch counts:", error);
      }
    }
    async function checkFollowing() {
      const authUser = await ProfileService.fetchAuthorData(
        authProvider.user.uuid
      );
      let url = `${authUser.host}authors/${authProvider.user.uuid}`;
      const encodedUrl = encodeURIComponent(url);
      const is_following = await FollowService.checkFollowing(
        userID,
        encodedUrl
      );
      setIsFollowing(is_following);
    }

    async function checkRequested() {
      // Re-initialize 
      setIsRequested(false);

      // Check inbox of the user ID
      const userInbox = await InboxService.getInbox(userID);
      await Promise.all(
        userInbox.map(async (item: any) => {
          if (item && item.type === "follow") {
            let actorId = item.actor.id.replace(/\/+$/, "").split("/").pop();
            if (actorId === authProvider.user.uuid) {
              setIsRequested(true);
            }
          }
        })
      );
    }

    fetchCounts();

    if (authProvider.isAuthenticated === false) {
      setIsAuthenticated(false);
      // this makes sure that the button for following/managing profile is displayed correctly
      setIsOwnProfile(false);
      fetchPosts(userID);
    } else {
      if (userID === authProvider.user.uuid) {
        setIsOwnProfile(true);
      } else {
        // this makes sure that the button for following/managing profile is displayed correctly
        setIsOwnProfile(false);
        checkRequested();
        checkFollowing();
      }
    }
  }, [userID, authProvider]);

  // Render loading indicator until authProvider is ready
  if (isAuthLoading) {
    return (
      <div className="loading">
        <CircularProgress sx={{ color: "#70ffaf" }} />
      </div>
    );
  }

  function getLink() {
    const currentURL = window.location.href;
    navigator.clipboard.writeText(currentURL);
    setOpenSnackbar(true);
  }

  async function handleButtonClick() {
    if (isFollowing) {
      // Displaying unfollow button
      await FollowService.unfollow(userID, authProvider.user);
      window.location.reload();
    } else {
      // Displaying follow button, send follower request
      const userResponse = await ProfileService.fetchAuthorData(
        authProvider.user.uuid
      );
      const followRequest = {
        type: "follow",
        summary: `${userResponse.displayName} wants to follow ${authorData.displayName}`,
        actor: {
          type: "author",
          id: `${userResponse.id}`,
          host: `${userResponse.host}`,
          displayName: `${userResponse.displayName}`,
          github: `${userResponse.github}`,
          page: `${userResponse.page}`,
        },
      };

      await InboxService.sendPostToInbox(userID, followRequest);
      setIsRequested(true);
    }
  }

  function handleManageProfileClick() {
    navigate("/profile");
  }

  function handleLoginClick() {
    navigate("/login");
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
                <Button
                  variant="contained"
                  color="primary"
                  size="small"
                  onClick={
                    isOwnProfile
                      ? handleManageProfileClick
                      : isAuthenticated
                      ? handleButtonClick
                      : handleLoginClick
                  }
                  disabled={isRequested}
                  sx={{ backgroundColor: "#70ffaf", color: "black" }}
                >
                  {isOwnProfile
                    ? "Manage Profile"
                    : isRequested
                    ? "Requested"
                    : isFollowing
                    ? "Unfollow"
                    : "Follow"}
                </Button>

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
                <p className={styles.username}>@{authorData.username ?? extractHost(authorData.host)}</p>

                <div className={styles.follows}>
                  <p className={styles.posts__count}>
                    <b>{postCount}</b> {postCount === 1 ? "post" : "posts"}
                  </p>
                  <p
                    className={styles.followers__count}
                    onClick={() =>
                      setfollowersModal({
                        open: true,
                        type: FollowerModalTypes.follower,
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
                        type: FollowerModalTypes.following,
                      })
                    }
                  >
                    <b>{followingCount}</b> following
                  </p>

                  <FollowList
                    isOpen={followersModal.open}
                    onClose={() =>
                      setfollowersModal({ open: false, type: "follower" })
                    }
                    isFollowerList={followersModal.type}
                    profileId={userID}
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
          {posts.map((post) => (
            <Post
              key={post.id}
              postGiven={post}
              canToggleComments={false}
              disableLikeComment={true}
            />
          ))}
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
