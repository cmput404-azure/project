// HomePage.jsx
import React, { useState, useEffect } from 'react';
import NavigationBar from "../NavigationBar/NavigationBar";
import PostBar from "../PostBar/PostBar";
import PostCard from "../PostCard/PostCard";
import AuthorPost from "../AuthorPost/AuthorPost";
import styles from './HomePage.module.scss'; // Assuming you are using SCSS modules

import logo from '../../images/dog_icon.png'

const HomePage = () => {
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true); // Adjust based on your authentication logic

    const handleNavClick = (item: string) => {
      console.log(`${item} clicked`);
      // Handle navigation actions here
    };
    const handleAddClick = () => {
        console.log('Add button clicked');
    };
  return (
    <div className={styles.homePage}>
      {/* First Section: Navigation Sidebar */}
      <div className={styles.navSection}>
            <NavigationBar onClick={handleNavClick} isLoggedIn={isLoggedIn} />
      </div>

      {/* Second Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar userImage= {logo} onAddClick={handleAddClick} />
        <PostCard
          profilePic="https://via.placeholder.com/50"
          userName="John Doe"
          postTime="2h ago"
          postContent="This is a sample post."
          postImage="https://via.placeholder.com/300"
          likeCount={123}
          saveCount={45}
          commentCount={67}
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
        />
      </div>

      {/* Third Section: Author Post */}
      <div className={styles.authorSection}>
      <AuthorPost authorImage= {logo}  authorName = "Kyle Quach" userName="tmquach.meomeo" postText= "The authors personal bio goes here, Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut." onAddClick={handleAddClick} />
      </div>
    </div>
  );
};

export default HomePage;
