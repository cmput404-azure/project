// HomePage.jsx
import { useEffect, useRef, useState } from "react";

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
      setPublicPosts(decodeBase64ToUrl(publicPosts));
      setNonPublicPosts(decodeBase64ToUrl(privatePosts));
      setIsLoading(false);
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

  // handle when the comment button is clicked
  const handleCommentButtonClick = (post: any) => {
    setIsCommentModalOpen(true);
    setSelectedPost(post);
    setCommentsList(post.comments.src);
  };
  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsCommentModalOpen(false);
    setSelectedPost(null);
  };

  const [activeFilterPost, setActiveFilterPost] = useState<ViewType>("all");
  function handleFilterPost(icon: ViewType) {
    setActiveFilterPost(icon);
  }

  if (isLoading)
    return (
      <div className={"loading"}>
        <CircularProgress sx={{color: "#70ffaf"}}/>
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
          <PostCard
            key={post.id}
            post={post}
            onCommentButtonClick={() => handleCommentButtonClick(post)}
          />
        ))}
      </div>

      {/* Comment Modal */}
      <CommentView
        isOpen={isCommentModalOpen}
        onRequestClose={handleCommentModalClose}
        postComponent={
          // find the post that was selected by uising the selectedPostID
          selectedPost &&
          displayedPosts.find((post) => post.id === selectedPost.id) ? (
            // pass in the selected post for the modal to display
            <PostCard key={selectedPost.id} post={selectedPost} />
          ) : null
        }
        comments={commentsList ? commentsList : []}
        author={user}
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
