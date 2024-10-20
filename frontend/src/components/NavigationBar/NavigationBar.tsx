import '@fortawesome/fontawesome-free/css/all.min.css';

import React, { useEffect, useState } from 'react';

import Modal from 'react-modal';
import NotificationList from '../NotificationList/NotificationList';
import UserSearch from '../UserSearch/UserSearch';
import { logout } from "../../util/auth/checkauth";
import styles from './NavigationBar.module.scss';

interface NavigationBarProps {
  onClick: (item: string) => void;
  isLoggedIn: boolean;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onClick, isLoggedIn }) => {
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false); // State to control the search modal
  const [isNotificationOpen, setIsNotificationOpen] = useState<boolean>(false); // State to control the search modal
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 600);

  const handleSearchClick = () => {
    setIsSearchOpen(true);
  };
  const handleNotificationsClick = () => {
    setIsNotificationOpen(true);
  }


  
  const commonNavigationItems = [
    { icon: <i className="fa-solid fa-house" />, label: 'home' },
    { icon: <i className="fa-solid fa-magnifying-glass" />, label: 'search' },
    { icon: <i className="fa-regular fa-bell" />, label: 'notifications' }
  ];

  const loggedInNavigationItems = [
    { icon: <i className="fa-solid fa-heart" />, label: 'likes' },
    { icon: <i className="fa-solid fa-comment-dots" />, label: 'messages' },
    { icon: <i className="fa-solid fa-sign-out" />, label: 'logout' },
  ];

  const loggedOutNavigationItems = [
    { icon: <i className="fa-solid fa-user" />, label: 'login' },
    { icon: <i className="fa-solid fa-user-plus" />, label: 'signup' },
  ];

  const bottomNavigationItems = [
    { icon: <i className="fas fa-user" />, label: 'profile' },
    { icon: <i className="fas fa-gear" />, label: 'settings' },
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
          {[...commonNavigationItems, ...(isLoggedIn ? loggedInNavigationItems : loggedOutNavigationItems), ...bottomNavigationItems].map((item) => (
            <div key={item.label} className={styles.navigationItem} onClick={() => {
              if (item.label === 'Search') {
                handleSearchClick();
              } else if (item.label === 'Notifications') {
                handleNotificationsClick(); // New handler for notifications
              } else {
                onClick(item.label); // Default handler for other items
              }
            }}>
              {item.icon}
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* For top 3 icons */}
          <div className={styles.iconGroup}>
            {commonNavigationItems.map((item) => (
              <div key={item.label} className={styles.navigationItem} onClick={() => {
                if (item.label === 'Search') {
                  handleSearchClick();
                } 
                else if (item.label === 'Notifications') {
                  handleNotificationsClick(); // New handler for notifications
                } 
                else if (item.label === 'logout') {
                  logout();
                }
                else {
                  onClick(item.label); // Default handler for other items
                }
              }}>
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
        <button className={styles.closeModalButton} onClick={() => setIsSearchOpen(false)}>Close</button>
        <UserSearch />
      </Modal>
      <Modal
        isOpen={isNotificationOpen}
        onRequestClose={() => setIsNotificationOpen(false)}
        contentLabel="Notifications"
        className={styles.ModalContent}
        overlayClassName={styles.Modal}
      >
        <button className={styles.closeModalButton} onClick={() => setIsNotificationOpen(false)}>Close</button>
        <NotificationList />
      </Modal>
    </nav>
  );
};

export default NavigationBar;
