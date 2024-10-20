// HomePage.jsx
import React, { useState, useEffect } from "react";
import NavigationBar from "../NavigationBar/NavigationBar";
import PostBar from "../PostBar/PostBar";
import PostCard from "../PostCard/PostCard";
import AuthorPost from "../AuthorPost/AuthorPost";
import CommentView from "../CommentView/CommentView";
import styles from "./HomePage.module.scss"; // Assuming you are using SCSS modules

import Modal from "react-modal";
import logo from "../../images/dog_icon.png";

// Modal needs this to be set so it knows where to put the modal in the DOM
Modal.setAppElement("#root");

const HomePage = () => {
  const [posts, setPosts] = useState<any[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);

  // Fetch public posts
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        // Fetch public posts
        const publicRes = await fetch("http://localhost:8000/api/stream/");
        const publicPosts = await publicRes.json();

        console.log(publicPosts);

        setPosts(publicPosts);
      } catch (err) {
        console.log(err)
        setError("Failed to fetch posts. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, []);
  

  const handleAddClick = () => {
    console.log("Add button clicked");
  };

  // handle when the comment button is clicked
  const handleCommentButtonClick = () => {
    setIsCommentModalOpen(true);
  };
  // handle when the comment modal is closed
  const handleCommentModalClose = () => {
    setIsCommentModalOpen(false);
  };

  // test comments
  const comments = [
    {
      id: 1,
      image: "https://via.placeholder.com/50",
      author: "Garfield",
      timePosted: "8h ago",
      text: "Great Success!",
    },
    {
      id: 2,
      image: "https://via.placeholder.com/50",
      author: "Douglas",
      timePosted: "10h ago",
      text: "Well Done!",
    },
  ];

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar userImage={logo} showButtonBar={false}/>
        {posts.map((post) => (
          <PostCard
            key={post.id}
            profilePic="https://via.placeholder.com/50"
            userName={post.author.displayName}
            postTime={new Date(post.published).toLocaleString()}
            postContent={post.content}
            postImage={post.has_image ? post.image : ""}
            likeCount={post.likes.length}
            saveCount={0}
            commentCount={post.comments.length}
            onCommentButtonClick={handleCommentButtonClick}
          />
        ))}

      </div>

      {/* Second Section: Author Post */}
      <div className={styles.authorSection}>
        <h2 className={styles.recommendedTitle} >Recommended Author</h2>
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
          <PostCard
            profilePic="https://via.placeholder.com/50"
            userName="John Doe"
            postTime="2h ago"
            postContent="This is a sample post."
            postImage="https://via.placeholder.com/300"
            likeCount={123}
            saveCount={45}
            commentCount={67}
            onCommentButtonClick={() => handleCommentButtonClick()}
          />
        }
        comments={comments}
      />
    </div>
  );
};

export default HomePage;
