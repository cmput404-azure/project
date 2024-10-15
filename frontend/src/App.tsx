import React from 'react';
import logo from './images/dog_icon.png';
import styles from './App.module.scss';

import PostBar from './components/PostBar/PostBar';
import AuthorPost from './components/AuthorPost/AuthorPost';

import PostCard from './components/PostCard/PostCard';
export default function App() {
  const handleAddClick = () => {
    console.log('Add button clicked');
  };

  return (
    <div className={styles.App}>
      Social distribution
      <PostCard ></PostCard>
      <PostBar userImage= {logo} onAddClick={handleAddClick} />
      <AuthorPost authorImage= {logo}  authorName = "Kyle Quach" userName="tmquach.meomeo" postText= "The authors personal bio goes here, Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut." onAddClick={handleAddClick} />
    </div>


  );
}

