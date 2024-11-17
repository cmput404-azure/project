import "@fortawesome/fontawesome-free/css/all.min.css";

import React, { useEffect, useState } from "react";
import CloseIcon from '@mui/icons-material/Close';
import Modal from "react-modal";
import NotificationList from "../NotificationList/NotificationList";
import UserSearch from "../UserSearch/UserSearch";
import styles from "./NavigationBar.module.scss";

interface NavigationBarProps {
  onClick: (item: string) => void;
  isLoggedIn: boolean;
  isAdmin: boolean
}

const NavigationBar: React.FC<NavigationBarProps> = ({
  onClick,
  isLoggedIn,
  isAdmin,
}) => {
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false); // State to control the search modal
  const [isNotificationOpen, setIsNotificationOpen] = useState<boolean>(false); // State to control the search modal
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 600);

  const handleSearchClick = () => {
    setIsSearchOpen(true);
  };
  const handleNotificationsClick = () => {
    setIsNotificationOpen(true);
  };

  const commonNavigationItems = [
    { icon: <i className="fa-solid fa-house" />, label: "home" },
    { icon: <i className="fa-solid fa-magnifying-glass" />, label: "search" },
  ];

  const loggedInNavigationItems = [
    { icon: <i className="fa-regular fa-bell" />, label: "notifications" },
    { icon: <i className="fa-solid fa-sign-out" />, label: "logout" },
  ];

  const loggedOutNavigationItems = [
    { icon: <i className="fa-solid fa-arrow-right-to-bracket" />, label: "login" },
  ];

  const bottomNavigationItems = [
    { icon: <i className="fas fa-user" />, label: "profile" },
  ];

  const adminNavigationItems = [
    { icon: <i className="fas fa-gear" />, label: "settings" },
  ]

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 600);
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <nav className={styles.navigationBar}>
      {/* This part for displaying nav bar in mobile mode is from Gemini - 10/10/2024 */}
      {isMobile ? (
        <div className={styles.iconGroup}>
          {[
            ...commonNavigationItems,
            ...(isLoggedIn
              ? [...bottomNavigationItems, ...loggedInNavigationItems, ]
              : loggedOutNavigationItems),
            ...(isAdmin && isLoggedIn ? adminNavigationItems : []),
          ].map((item) => (
            <div
              key={item.label}
              className={styles.navigationItem}
              onClick={() => {
                if (item.label === "search") {
                  handleSearchClick();
                } else if (item.label === "notifications") {
                  handleNotificationsClick();
                } else {
                  onClick(item.label); // Default handler for other items
                }
              }}
            >
              {item.icon}
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* For top 3 icons */}
          <div className={styles.iconGroup}>
            {commonNavigationItems.map((item) => (
              <div
                key={item.label}
                className={styles.navigationItem}
                onClick={(e) => {
                  e.preventDefault();
                  if (item.label === "search") {
                    handleSearchClick();
                  } else {
                    onClick(item.label); // Default handler for other items
                  }
                }}
              >
                {item.icon}
              </div>
            ))}
            {isLoggedIn &&
              loggedInNavigationItems.map((item) => (
                <div
                  key={item.label}
                  className={styles.navigationItem}
                  onClick={() => {
                    if (item.label === "notifications") {
                      handleNotificationsClick();
                    } else {
                      onClick(item.label);
                    }
                  }
                  }
                >
                  {item.icon}
                </div>
              ))}
          </div>
          {/* For Bottom Navigation */}
          <div className={styles.bottomIconGroup}>
          {isLoggedIn ? (
            bottomNavigationItems.map((item) => (
              <div
                key={item.label}
                className={styles.navigationItem}
                onClick={() => onClick(item.label)}
              >
                {item.icon}
              </div>
            ))
          ) : (
            loggedOutNavigationItems
              .filter((item) => item.label === "login")
              .map((item) => (
                <div
                  key={item.label}
                  className={styles.navigationItem}
                  onClick={() => onClick(item.label)}
                >
                  {item.icon}
                </div>
              ))
          )}
          {/* For Settings Icon */}
            {isAdmin && adminNavigationItems.map((item) => (
              <div
                key={item.label}
                className={styles.navigationItem}
                onClick={() => onClick(item.label)}
              >
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
        className={styles.modalContent}
        overlayClassName={styles.modalOverlay}
      >
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>User Search</h2>
          <button
            className={styles.closeModalButton}
            onClick={() => setIsSearchOpen(false)}
          >
            <CloseIcon style={{ fontSize: "14px" }} />
          </button>
        </div>
        <UserSearch closeModal={() => setIsSearchOpen(false)} />
      </Modal>
      <Modal
        isOpen={isNotificationOpen}
        onRequestClose={() => setIsNotificationOpen(false)}
        contentLabel="Notifications"
        className={styles.modalContent}
        overlayClassName={styles.modalOverlay}
      >
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Notifications</h2>
          <button
            className={styles.closeModalButton}
            onClick={() => setIsNotificationOpen(false)}
          >
            <CloseIcon style={{ fontSize: "14px" }} />
          </button>
        </div>
        <NotificationList />
      </Modal>
    </nav>
  );
};

export default NavigationBar;
