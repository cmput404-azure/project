import '@fortawesome/fontawesome-free/css/all.min.css';

import React, { useEffect, useState } from 'react';

import styles from './NavigationBar.module.scss';

interface NavigationBarProps {
  onClick: (item: string) => void;
  isLoggedIn: boolean;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onClick, isLoggedIn }) => {
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 600);

  const commonNavigationItems = [
    { icon: <i className="fa-solid fa-house"/>, label: 'Home' },
  ];

  const loggedInNavigationItems = [
    { icon: <i className="fa-solid fa-heart"/>, label: 'Likes' },
    { icon: <i className="fa-solid fa-comment-dots"/>, label: 'Messages' },
  ];

  const bottomNavigationItems = [
    { icon: <i className="fas fa-user"/>, label: 'Profile' },
    { icon: <i className="fas fa-gear"/>, label: 'Settings' },
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
              <div key={item.label} className={styles.navigationItem} onClick={() => onClick(item.label)}>
                {item.icon}
              </div>
          ))}
        </div>
      ) : (
        <>
          {/* For top 3 icons */}
          <div className={styles.iconGroup}>
            {commonNavigationItems.map((item) => (
              <div key={item.label} className={styles.navigationItem} onClick={() => onClick(item.label)}>
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
    </nav>
  );
};

export default NavigationBar;
