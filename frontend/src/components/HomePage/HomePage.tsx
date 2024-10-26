// HomePage.jsx
import { useEffect, useState } from "react";

import AuthorPost from "../AuthorPost/AuthorPost";
import CommentView from "../CommentView/CommentView";
import Modal from "react-modal";
import PostBar from "../PostBar/PostBar";
import PostCard from "../PostCard/PostCard";
import logo from "../../images/dog_icon.png";
import stream from "../../service/stream";
import styles from "./HomePage.module.scss";
import { useAuth } from "../../state";
import { api } from "../../service/config";

import { decodeBase64ToUrl } from "../../util/rendering/decodeBase64ToUrl";

// Modal needs this to be set so it knows where to put the modal in the DOM
Modal.setAppElement("#root");

type ViewType = "all" | "unlisted_friends-only";
const HomePage = () => {
  const [publicPosts, setPublicPosts] = useState<any[]>([]);
  const [nonPublicPosts, setNonPublicPosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<any | null>(null);
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

  useEffect(() => {
    const fetchPosts = async () => {
      if (isUserLoading) return; // Wait until user data is loaded

      try {
        const publicPosts = await stream.getStream();
        const privatePosts = await stream.getStream(true);

        setNonPublicPosts(decodeBase64ToUrl(privatePosts as any[]));
        setPublicPosts(decodeBase64ToUrl(publicPosts as any[]));
        setIsLoading(false);
      } catch (err) {
        console.log(err);
        setError("Failed to fetch posts. Please try again.");
      }
    };
    fetchPosts();
  }, [isUserLoading]); // Run when user loading state changes

  const handleAddClick = () => {
    console.log("Add button clicked");
  };

  // handle when the comment button is clicked
  const handleCommentButtonClick = (post: any) => {
    setIsCommentModalOpen(true);
    setSelectedPost(post);
  };
  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsCommentModalOpen(false);
    setSelectedPost(null);
  };

  // test comments
  const comments = [
    {
      id: 1,
      image: `https://ui-avatars.com/api/?background=random&name=${"Garfield"}`,
      author: "Garfield",
      timePosted: "8h ago",
      text: "Great Success!",
    },
    {
      id: 2,
      image: `https://ui-avatars.com/api/?background=random&name=${"Douglas"}`,
      author: "Douglas",
      timePosted: "10h ago",
      text: "Well Done!",
    },
  ];

  const [activeFilterPost, setActiveFilterPost] = useState<ViewType>("all");
  function handleFilterPost(icon: ViewType) {
    setActiveFilterPost(icon);
  }

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  const displayedPosts =
    activeFilterPost === "all" ? publicPosts : nonPublicPosts;

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar showButtonBar={false} author={user} />
        {authProvider.isAuthenticated && (
          <div className={styles["icon-bar"]}>
            <div
              className={`${styles["icon-section"]} ${
                activeFilterPost === "all" ? styles.active : ""
              }`}
              onClick={() => handleFilterPost("all")}
            >
              <i className={`${styles.icon} ${styles["public-icon"]}`}></i>
            </div>
            <div className={styles["vertical-divider"]}></div>
            <div
              className={`${styles["icon-section"]} ${
                activeFilterPost === "unlisted_friends-only"
                  ? styles.active
                  : ""
              }`}
              onClick={() => handleFilterPost("unlisted_friends-only")}
            >
              <i className={`${styles.icon} ${styles["friend-icon"]}`}></i>
            </div>
          </div>
        )}
        {displayedPosts.map((post) => (
          <PostCard
            key={post.id}
            userID={post.author.id}
            profilePic={post.author.profileImage}
            userName={post.author.displayName}
            postTime={new Date(post.published).toLocaleString()}
            postContent={post.content}
            // postImage={post.has_image ? post.image : ""}
            likeCount={post.likes.length}
            saveCount={0}
            commentCount={post.comments.length}
            onCommentButtonClick={() => handleCommentButtonClick(post)}
            onClick={() => handleCommentButtonClick(post)}
          />
        ))}
      </div>

      {/* Second Section: Author Post */}
      <div className={styles.authorSection}>
        <h2 className={styles.recommendedTitle}>Recommended Author</h2>
        <AuthorPost
          authorImage={logo}
          authorName="Kyle Quach"
          userName="tmquach.meomeo"
          postText="The authors personal bio goes here, Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut."
          onAddClick={handleAddClick}
        />
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
            <PostCard
              key={selectedPost.id}
              userID={selectedPost.author.id}
              profilePic={
                selectedPost.author?.profileImage ||
                `https://ui-avatars.com/api/?background=random&name=${selectedPost.author?.displayName}`
              }
              userName={selectedPost.author.displayName}
              postTime={new Date(selectedPost.published).toLocaleString()}
              postContent={selectedPost.content}
              // postImage={""}
              likeCount={0}
              saveCount={0}
              commentCount={0}
            />
          ) : null
        }
        comments={comments}
        author={user}
      />
    </div>
  );
};

export default HomePage;
