import React, { useState } from 'react';
import styles from './PostBar.module.scss';

interface PostBarProps {
  userImage: string;
  onAddClick: () => void;
}

type IconType = 'earth' | 'people' | 'link';

const PostBar: React.FC<PostBarProps> = ({ userImage, onAddClick }) => {
  const [activeIcon, setActiveIcon] = useState<IconType>('earth');

  const handleIconClick = (icon: IconType) => {
    setActiveIcon(icon);
  };

  const handlePostClick = () => {
    console.log('Post button clicked');
  };

  return (
    <div className={styles.container}>
      <section className={styles['post-bar']}>
        <img src={userImage} alt="User" className={styles['user-image']} />
        <div className={styles['vertical-divider']}></div>
        <input type="text" placeholder="Type Something" className={styles['post-input']} />
        <button className={styles['add-button']} onClick={onAddClick}>
          <span>+</span>
        </button>
      </section>
      <section className={styles['button-bar']}>
        <div className={styles['icon-bar']}>
          <div
            className={`${styles['icon-section']} ${activeIcon === 'earth' ? styles.active : ''}`}
            onClick={() => handleIconClick('earth')}
          >
            <i className={`${styles.icon} ${styles['earth-icon']}`}></i>
          </div>
          <div className={styles['vertical-divider']}></div>
          <div
            className={`${styles['icon-section']} ${activeIcon === 'people' ? styles.active : ''}`}
            onClick={() => handleIconClick('people')}
          >
            <i className={`${styles.icon} ${styles['people-icon']}`}></i>
          </div>
          <div className={styles['vertical-divider']}></div>
          <div
            className={`${styles['icon-section']} ${activeIcon === 'link' ? styles.active : ''}`}
            onClick={() => handleIconClick('link')}
          >
            <i className={`${styles.icon} ${styles['link-icon']}`}></i>
          </div>
        </div>
        <button className={styles['post-button']} onClick={handlePostClick}>
          Post
        </button>
      </section>
    </div>
  );
};

export default PostBar;



// import React from 'react';
// import logo from './images/dog_icon.png';
// import styles from './App.module.scss';

// import PostBar from './components/PostBar/PostBar';
// import AuthorPost from './components/AuthorPost/AuthorPost';

// import PostCard from './components/PostCard/PostCard';
// export default function App() {
//   const handleAddClick = () => {
//     console.log('Add button clicked');
//   };

//   return (
//     <div className={styles.App}>
//       Social distribution
//       <PostBar userImage= {logo} onAddClick={handleAddClick} />
//       <AuthorPost authorImage= {logo}  authorName = "Kyle Quach" userName="tmquach.meomeo" postText= "The authors personal bio goes here, Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut." onAddClick={handleAddClick} />
//     </div>


//   );
// }
