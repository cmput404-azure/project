import { Route, Routes, useNavigate } from "react-router-dom";

import ErrorPage from "./error-page";
import NavigationBar from "./components/NavigationBar/NavigationBar";
import Root from "./routes/Root";
import UserProfile from "./components/UserProfile/UserProfile";
import styles from './App.module.scss';
import HomePage from "./components/HomePage/HomePage";
export default function App() {
  const nav = useNavigate();

  return (
    <div className={styles.App}>
        <NavigationBar onClick={(item) => nav(`/${item}`)} isLoggedIn={false} />

        <div className={styles.content}>
          <Routes>
            <Route path="/" element={<HomePage/>} />
            <Route path="/home" element={<HomePage/>} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/settings" element={<Root />} />
            <Route path="*" element={<ErrorPage />} />
          </Routes>
        </div>
    </div>
  );
}

