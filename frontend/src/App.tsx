import Auth, { Logout } from "./components/Auth/Auth";
import { Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

import ErrorPage from "./error-page";
import HomePage from "./components/HomePage/HomePage";
import NavigationBar from "./components/NavigationBar/NavigationBar";
import Root from "./routes/Root";
import UserProfile from "./components/UserProfile/UserProfile";
import { checkAuth } from "./util/auth/checkauth";
import styles from './App.module.scss';

export default function App() {
  const nav = useNavigate();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userUUID, setUserUUID] = useState<string>("");

  useEffect(() => {
    checkAuth().then((data) => {
      setIsLoggedIn(data.is_authenticated);
      console.log(data);
      setUserUUID(data.uuid);
    });
  })
  return (
    <div className={styles.App}>
        <NavigationBar onClick={(item) => nav(`/${item}`)} isLoggedIn={isLoggedIn} />

        <div className={styles.content}>
          <Routes>
            <Route path="/" element={<HomePage isLoggedIn={isLoggedIn} userUUID={userUUID}/>} />
            <Route path="/home" element={<HomePage isLoggedIn={isLoggedIn} userUUID={userUUID}/>} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/settings" element={<Root />} />
            <Route path="/login" element={<Auth />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="*" element={<ErrorPage />} />
          </Routes>
        </div>
    </div>
  );
}

