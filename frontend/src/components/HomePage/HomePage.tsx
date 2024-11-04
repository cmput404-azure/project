// HomePage.jsx
import { useEffect, useState } from "react";

import { CircularProgress } from "@mui/material";
import CommentView from "../CommentView/CommentView";
import PeopleIcon from "@mui/icons-material/People";
import PostBar from "../PostBar/PostBar";
import PostCard from "../PostCard/PostCard";
import PublicIcon from "@mui/icons-material/Public";
import { api } from "../../service/config";
import { decodeBase64ToUrl } from "../../util/rendering/decodeBase64ToUrl";
import stream from "../../service/stream";
import styles from "./HomePage.module.scss";
import { useAuth } from "../../state";
import Post from "../Post/Post";

type ViewType = "all" | "unlisted_friends-only";
const HomePage = () => {
  const [publicPosts, setPublicPosts] = useState<any[]>([]);
  const [nonPublicPosts, setNonPublicPosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<any | null>(null);
  const [commentsList, setCommentsList] = useState<any[]>([]);
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
      const publicPosts = await stream.getStream();
      const privatePosts = await stream.getStream(true);
      const decodedPublicPosts = decodeBase64ToUrl(publicPosts);
      const decodedNonPublicPosts = decodeBase64ToUrl(privatePosts);
      setPublicPosts(decodedPublicPosts);
      setNonPublicPosts(decodedNonPublicPosts);

      setIsLoading(false);
      return {
        publicPosts: decodedPublicPosts,
        nonPublicPosts: decodedNonPublicPosts,
      };
    } catch (err) {
      console.log(err);
      setError("Failed to fetch posts. Please try again.");
      return { publicPosts: [], nonPublicPosts: [] };
    }
  };

  useEffect(() => {
    fetchPosts();
    const interval = setInterval(fetchPosts, 60000);
    return () => clearInterval(interval); // Clean up the interval on component unmount
  }, [isUserLoading]);

  // handle when the comment button is clicked
  // const handleCommentButtonClick = (post: any) => {
  //   setIsCommentModalOpen(true);
  //   setSelectedPost(post);
  //   setCommentsList(post.comments.src);
  // };

  const handleCommentButtonClick = async (post) => {
    try {
      // Fetch posts and get the latest public and non-public posts
      const { publicPosts, nonPublicPosts } = await fetchPosts();

      // Search for the post in the freshly fetched posts
      const allPosts = [...publicPosts, ...nonPublicPosts];
      const foundPost = allPosts.find((p) => p.id === post.id);

      if (foundPost) {
        setSelectedPost(foundPost);
        setCommentsList(foundPost.comments.src); // Set the comments list from the found post
      } else {
        setError("Post not found.");
      }

      setIsCommentModalOpen(true);
    } catch (err) {
      console.error("Error refetching posts:", err);
      setError("Failed to fetch posts. Please try again.");
    }
  };

  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsCommentModalOpen(false);
    setSelectedPost(null);
  };

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
      </div>

      {/* Comment Modal */}
      <CommentView
        isOpen={isCommentModalOpen}
        onRequestClose={handleCommentModalClose}
        post={selectedPost}
      />
    </div>
  );
};

export default HomePage;

{
  /* Second Section: Author Post */
}
{
  /* <div className={styles.authorSection}>
        <h2 className={styles.recommendedTitle}>Recommended Author</h2>
        <AuthorPost
          authorImage={logo}
          authorName="Kyle Quach"
          userName="tmquach.meomeo"
          postText="The authors personal bio goes here, Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut."
          onAddClick={handleAddClick}
        />
      </div> */
}
