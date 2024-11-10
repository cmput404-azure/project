import { Button, CircularProgress } from "@mui/material";
// HomePage.jsx
import { useEffect, useState } from "react";

import PeopleIcon from "@mui/icons-material/People";
import Post from "../Post/Post";
import PostBar from "../PostBar/PostBar";
import PublicIcon from "@mui/icons-material/Public";
import { api } from "../../service/config";
import stream from "../../service/stream";
import styles from "./HomePage.module.scss";
import { useAuth } from "../../state";

type ViewType = "all" | "unlisted_friends-only";
const HomePage = () => {
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

  const fetchPosts = async (
    publicPage = 1,
    privatePage = 1,
  ) => {
    if (isUserLoading) return;
  
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

    } catch (err) {
      console.log(err);
      setError("Failed to fetch posts. Please try again.");
    }
  };

  useEffect(() => {
    fetchPosts(publicPage, privatePage); // fetch initial
    const interval = setInterval(() => {
      fetchPosts(publicPage, privatePage);
    }, 60000);
    return () => clearInterval(interval); // Clean up the interval on component unmount
  }, [isUserLoading, privatePage, publicPage]);

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
          <Post
            key={post.type === "shared" ? `${post.id}-${post.shared_by}` : post.id}
            postGiven={post}
            canToggleComments={false}
          />
        ))}
        {displayedPosts.length === 0 && (
          <div className={styles.noPosts}>
            <p>There are no posts on this node 🫨</p>
          </div>
        )}
        {activeFilterPost === "all" && publicPage < totalPublicPages && (
          <Button
            variant="contained"
            onClick={nextPublicPage}
            disabled={isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {isLoading ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}

        {activeFilterPost === "unlisted_friends-only" && privatePage < totalPrivatePages && (
          <Button
            variant="contained"
            onClick={nextPrivatePage}
            disabled={isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {isLoading ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}
      </div>
    </div>
  );
};

export default HomePage;
