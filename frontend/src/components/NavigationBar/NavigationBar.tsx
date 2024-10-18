import '@fortawesome/fontawesome-free/css/all.min.css';

import React, { useEffect, useState } from 'react';
import UserSearch from '../UserSearch/UserSearch';
import styles from './NavigationBar.module.scss';
import Modal from 'react-modal';

interface NavigationBarProps {
  onClick: (item: string) => void;
  isLoggedIn: boolean;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onClick, isLoggedIn }) => {
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false); // State to control the search modal

  const handleSearchClick = () => {
    setIsSearchOpen(true);
  };
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 600);

  const commonNavigationItems = [
    { icon: <i className="fa-solid fa-house" />, label: 'Home' },
    { icon: <i className="fa-solid fa-magnifying-glass" />, label: 'Search' },

  ];

  const loggedInNavigationItems = [
    { icon: <i className="fa-solid fa-heart" />, label: 'Likes' },
    { icon: <i className="fa-solid fa-comment-dots" />, label: 'Messages' },
  ];

  const bottomNavigationItems = [
    { icon: <i className="fas fa-user" />, label: 'Profile' },
    { icon: <i className="fas fa-gear" />, label: 'Settings' },
  ];

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 600);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <nav className={styles.navigationBar}>
      {/* This part for displaying nav bar in mobile mode is from Gemini - 10/10/2024 */}
      {isMobile ? (
        <div className={styles.iconGroup}>
          {[...commonNavigationItems, ...(isLoggedIn ? loggedInNavigationItems : []), ...bottomNavigationItems].map((item) => (
            <div key={item.label} className={styles.navigationItem} onClick={() => item.label === 'Search' ? handleSearchClick() : onClick(item.label)}>
              {item.icon}
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* For top 3 icons */}
          <div className={styles.iconGroup}>
            {commonNavigationItems.map((item) => (
              <div key={item.label} className={styles.navigationItem} onClick={() => item.label === 'Search' ? handleSearchClick() : onClick(item.label)}>
                {item.icon}
              </div>
            ))}
            {isLoggedIn && loggedInNavigationItems.map((item) => (
              <div key={item.label} className={styles.navigationItem} onClick={() => onClick(item.label)}>
                {item.icon}
              </div>
            ))}
          </div>
          {/* For bottom 2 icons */}
          <div className={styles.bottomIconGroup}>
            {bottomNavigationItems.map((item) => (
              <div key={item.label} className={styles.navigationItem} onClick={() => onClick(item.label)}>
                {item.icon}
              </div>
            ))}
          </div>
        </>
      )}
      <Modal
        isOpen={isSearchOpen}
        onRequestClose={() => setIsSearchOpen(false)}
        contentLabel="User Search"
        className={styles.ModalContent} 
        overlayClassName={styles.Modal}
      >
        <button className = {styles.closeModalButton} onClick={() => setIsSearchOpen(false)}>Close</button>
        <UserSearch />
      </Modal>
    </nav>
  );
};

export default NavigationBar;
