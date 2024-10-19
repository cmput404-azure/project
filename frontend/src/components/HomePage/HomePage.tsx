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
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true); // Adjust based on your authentication logic
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);

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

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar userImage={logo} />
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
      </div>

      {/* Second Section: Author Post */}
      <div className={styles.authorSection}>
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
