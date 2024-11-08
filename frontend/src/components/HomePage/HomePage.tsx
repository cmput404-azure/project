import { CircularProgress, Modal } from "@mui/material";
// HomePage.jsx
import { useEffect, useState } from "react";

import PeopleIcon from "@mui/icons-material/People";
import Post from "../Post/Post";
import PostBar from "../PostBar/PostBar";
import PublicIcon from "@mui/icons-material/Public";
import { api } from "../../service/config";
import { decodeBase64ToUrl } from "../../util/rendering/decodeBase64ToUrl";
import stream from "../../service/stream";
import styles from "./HomePage.module.scss";
import { useAuth } from "../../state";

type ViewType = "all" | "unlisted_friends-only";
const HomePage = () => {
  const [publicPosts, setPublicPosts] = useState<any[]>([]);
  const [nonPublicPosts, setNonPublicPosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const authProvider = useAuth();

  const [isUserLoading, setIsUserLoading] = useState(true);

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
        console.log(err);
        setError("Failed to fetch user data.");
        setIsUserLoading(false);
      }
    };

    fetchUser();
  }, [authProvider.user]); // This effect runs when authProvider.user changes

  const fetchPosts = async () => {
    if (isUserLoading) return;

    try {
      // Fetch paginated data for the requested page
      const publicPosts = await stream.getStream();
      const privatePosts = await stream.getStream(true); // this returns PaginatedResponse type

      const decodedPublicPosts = decodeBase64ToUrl(publicPosts.src);
      const decodedNonPublicPosts = decodeBase64ToUrl(privatePosts.src);

      setPublicPosts(decodedPublicPosts);
      setNonPublicPosts(decodedNonPublicPosts);
      setIsLoading(false);

      return {
        publicPosts: decodedPublicPosts,
        nonPublicPosts: decodedNonPublicPosts
      }
      
    } catch (err) {
      console.log(err);
      setError("Failed to fetch posts. Please try again.");
    }
  };

  useEffect(() => {
    fetchPosts();
    const interval = setInterval(fetchPosts, 60000);
    return () => clearInterval(interval); // Clean up the interval on component unmount
  }, [isUserLoading]);

  const [activeFilterPost, setActiveFilterPost] = useState<ViewType>("all");
  function handleFilterPost(icon: ViewType) {
    setActiveFilterPost(icon);
    fetchPosts();
  }

  if (isLoading)
    return (
      <div className={"loading"}>
        <CircularProgress sx={{ color: "#70ffaf" }} />
      </div>
    );
  if (error) return <p>{error}</p>;

  const displayedPosts =
    activeFilterPost === "all" ? publicPosts : nonPublicPosts;

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar fetchPosts={fetchPosts} author={user} />
        {authProvider.isAuthenticated && (
          <div className={styles.icon_bar}>
            <div
              className={`${styles.icon_section} ${
                activeFilterPost === "all" ? styles.active : ""
              }`}
              onClick={() => handleFilterPost("all")}
            >
              <PublicIcon className={styles.icon} />
            </div>
            <div
              className={`${styles.icon_section} ${
                activeFilterPost === "unlisted_friends-only"
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
          <Post key={post.id} postGiven={post} canToggleComments={false} />
        ))}
        {displayedPosts.length === 0 && (
          <div className={styles.noPosts}>
            <p>There are no posts on this node 🫨</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
