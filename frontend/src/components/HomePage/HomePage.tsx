import { Button, CircularProgress, Drawer } from "@mui/material";
import { useEffect, useState } from "react";

import { Author } from "../../models/models";
import AuthorPost from "../AuthorPost/AuthorPost";
import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';
import PeopleIcon from "@mui/icons-material/People";
import Post from "../Post/Post";
import PostBar from "../PostBar/PostBar";
import PublicIcon from "@mui/icons-material/Public";
import _ from 'lodash';
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import follow from "../../service/follow";
import profileService from "../../service/profile";
import stream from "../../service/stream";
import styles from "./HomePage.module.scss";
import { useAuth } from "../../state";

type ViewType = "all" | "unlisted_friends-only";

const HomePage = () => {
  const [recommended, setRecommended] = useState<Author[]>([]); // list of remote authors for now, but should make it local if no remote connection, and make sure it's only people
  const [recommendedDrawer, setRecommendedDrawer] = useState<boolean>(false);
  const [publicPosts, setPublicPosts] = useState<any[]>([]);
  const [privatePosts, setPrivatePosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [activeFilterPost, setActiveFilterPost] = useState<ViewType>("all");
  const [publicPage, setPublicPage] = useState(1); // so we can use the pagination feature
  const [privatePage, setPrivatePage] = useState(1);
  const [totalPublicPages, setTotalPublicPages] = useState(0);
  const [totalPrivatePages, setTotalPrivatePages] = useState(0);
  const pageSize = 15;
  const authProvider = useAuth();
  const [isInitial, setIsInitial] = useState(true);

  const [isUserLoading, setIsUserLoading] = useState(true);
  const [pageLoading, setPageLoading] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      if (!authProvider.user) {
        setIsUserLoading(false); // user not authenticated
        return;
      }

      try {
        const authorReq = await api.get(
          `/api/authors/${authProvider.user.uuid}/`
        );
        setUser(authorReq.data);
        setIsUserLoading(false);
      } catch (err) {
        setError("Failed to fetch user data.");
        setIsUserLoading(false);
      }
    };

    const fetchRecommended = async () => {
      try {
        if (!authProvider.user) {
          setIsUserLoading(false); // user not authenticated
          return;
        }
        // Get users haven't followed
        const following = await follow.getFollowing(authProvider.user.uuid);
        const allUsers = await profileService.fetchAllAuthors()

        // Filter out all users that current user already follows
        const followingIds = new Set(following.map((following) => following.id));
        const strangers = allUsers.filter(
          (user) =>
            !followingIds.has(user.id) &&
            extractUUID(user.id) !== authProvider.user.uuid &&
            user.type !== "node"
        );

        // Get all the remote authors
        const remoteUsers = await profileService.fetchRecommendedAuthors();
        setRecommended(_.shuffle([...strangers, ...remoteUsers]));

      } catch (err) {
        console.error("Something went wrong: ", err);
      }
    }

    fetchUser();
    fetchRecommended();
  }, [authProvider.user]); // This effect runs when authProvider.user changes

  const fetchPosts = async (
    publicPage = 1,
    privatePage = 1,
  ) => {
    if (isUserLoading) return;

    setPageLoading(true);

    try {
      const publicResponse = await stream.getStream(false, publicPage);
      const privateResponse = await stream.getStream(true, privatePage);

      setPublicPosts(prevPosts => {
        const existingIds = new Set(prevPosts.map(post => post.id));
        const newPublicPosts = publicResponse.src.filter(post => !existingIds.has(post.id));
        const latestExistingDate = new Date(Math.max(...prevPosts.map(post => new Date(post.published).getTime())));
        const newerPosts = newPublicPosts.filter(post => new Date(post.published).getTime() > latestExistingDate.getTime()); // the ones created from PostBar
        const filteredPosts = newPublicPosts.filter(post => !newerPosts.some(newPost => newPost.id === post.id)); // don't want duplicate
        return [...newerPosts, ...prevPosts, ...filteredPosts];
      });

      setPrivatePosts(prevPosts => {
        const existingIds = new Set(prevPosts.map(post => post.id));
        const newPrivatePosts = privateResponse.src.filter(post => !existingIds.has(post.id));
        const latestExistingDate = new Date(Math.min(...prevPosts.map(post => new Date(post.published).getTime())));
        const newerPosts = newPrivatePosts.filter(post => new Date(post.published).getTime() > latestExistingDate.getTime());
        const filteredPosts = newPrivatePosts.filter(post => !newerPosts.some(newPost => newPost.id === post.id));
        return [...newerPosts, ...prevPosts, ...filteredPosts];
      });

      setTotalPublicPages(Math.ceil(publicResponse.count / pageSize));
      setTotalPrivatePages(Math.ceil(privateResponse.count / pageSize));

      setIsLoading(false);
      setPageLoading(false);

    } catch (err) {
      setError("Failed to fetch posts. Please try again.");
    }
  };

  useEffect(() => {
    fetchPosts(publicPage, privatePage);
    const interval = setInterval(() => {
      fetchPosts(publicPage, privatePage);
    }, 5000);
    return () => clearInterval(interval);
  }, [isUserLoading, privatePage, publicPage, activeFilterPost]);

  useEffect(() => {
    if (isInitial) {
      setIsInitial(false);
      return;
    }
    fetchPosts(publicPage, privatePage);
  }, [activeFilterPost]);

  const nextPublicPage = async () => {
    if (isLoading || publicPage >= totalPublicPages) return;
    setPublicPage(prevPage => prevPage + 1);
  }

  const nextPrivatePage = async () => {
    if (isLoading || privatePage >= totalPrivatePages) return;
    setPrivatePage(prevPage => prevPage + 1);
  }

  function handleFilterPost(icon: ViewType) {
    setActiveFilterPost(icon);
  }

  if (isLoading)
    return (
      <div className={"loading"}>
        <CircularProgress sx={{ color: "#70ffaf" }} />
      </div>
    );
  if (error) return <p>{error}</p>;

  const displayedPosts = activeFilterPost === "all" ? publicPosts : privatePosts;

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar fetchPosts={fetchPosts} author={user} />
        {authProvider.isAuthenticated && (
          <div className={styles.icon_bar}>
            <div
              className={`${styles.icon_section} ${activeFilterPost === "all" ? styles.active : ""
                }`}
              onClick={() => handleFilterPost("all")}
            >
              <PublicIcon className={styles.icon} />
            </div>
            <div
              className={`${styles.icon_section} ${activeFilterPost === "unlisted_friends-only"
                ? styles.active
                : ""
                }`}
              onClick={() => handleFilterPost("unlisted_friends-only")}
            >
              <PeopleIcon className={styles.icon} />
            </div>
          </div>
        )}
        {displayedPosts.map((post) => (
          <Post
            key={post.type === "shared" ? `${post.id}-${post.shared_by}` : post.id}
            postGiven={post}
            canToggleComments={false}
          />
        ))}
        {displayedPosts.length === 0 && (
          <div className={styles.noPosts}>
            <p>It's a little quiet here...</p>
            <p>Break the silence — create the first post!</p>
          </div>
        )}
        {activeFilterPost === "all" && publicPage < totalPublicPages && (
          <Button
            variant="contained"
            onClick={nextPublicPage}
            disabled={pageLoading || isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {(pageLoading || isLoading) ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}

        {activeFilterPost === "unlisted_friends-only" && privatePage < totalPrivatePages && (
          <Button
            variant="contained"
            onClick={nextPrivatePage}
            disabled={pageLoading || isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {(pageLoading || isLoading) ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}
      </div>


      {authProvider.isAuthenticated &&
        <div className={styles.drawer}>
          <Button className={styles.recommended__button} size="small" onClick={() => setRecommendedDrawer(true)}>
            <KeyboardDoubleArrowLeftIcon />
          </Button>
          <Drawer
            open={recommendedDrawer}
            anchor="right"
            onClose={() => setRecommendedDrawer(false)}
            PaperProps={{
              sx: { bgcolor: "rgba(0,0,0,0)", color: "#fff" },
            }}
          >
            <RecommendedAuthors authors={recommended} />
          </Drawer>
        </div>
      }
    </div>
  );
};

export default HomePage;

export function RecommendedAuthors({ authors }: { authors: Author[] }) {
  return (
    <div className={styles.recommended}>
      <h2 className={styles.recommendedTitle}>Recommended for you</h2>
      {authors.map((author) => (
        <AuthorPost key={author.id} author={author} />
      ))}
    </div>
  );
}
