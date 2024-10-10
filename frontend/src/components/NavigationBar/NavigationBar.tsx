import React, { useEffect, useState } from 'react';
import styles from './NavigationBar.module.css';
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined';
import FavoriteBorderOutlinedIcon from '@mui/icons-material/FavoriteBorderOutlined';
import ChatOutlinedIcon from '@mui/icons-material/ChatOutlined';
import Person2OutlinedIcon from '@mui/icons-material/Person2Outlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';

interface NavigationBarProps {
  onClick: (item: string) => void;
  isLoggedIn: boolean;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onClick, isLoggedIn }) => {
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 600);

  const commonNavigationItems = [
    { icon: <HomeOutlinedIcon />, label: 'Home' },
  ];

  const loggedInNavigationItems = [
    { icon: <FavoriteBorderOutlinedIcon />, label: 'Likes' },
    { icon: <ChatOutlinedIcon />, label: 'Messages' },
  ];

  const bottomNavigationItems = [
    { icon: <Person2OutlinedIcon />, label: 'Profile' },
    { icon: <SettingsOutlinedIcon />, label: 'Settings' },
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
