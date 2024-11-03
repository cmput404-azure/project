import Auth, { Logout } from "./components/Auth/Auth";
import { Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

import { CircularProgress } from "@mui/material";
import ErrorPage from "./error-page";
import HomePage from "./components/HomePage/HomePage";
import NavigationBar from "./components/NavigationBar/NavigationBar";
import Post from "./components/Post/Post";
import ProtectedRoute from "./routes/ProtectedRoute";
import PublicProfile from "./components/PublicProfile/PublicProfile";
import Root from "./routes/Root";
import UserProfile from "./components/UserProfile/UserProfile";
import UserProfile2 from "./components/UserProfile/UserProfile2";
import styles from "./App.module.scss";
import { useAuth } from "./state";

export default function App() {
  const nav = useNavigate();
  const authProvider = useAuth();

  if (authProvider.loading) {
    return <div className={"loading"}><CircularProgress sx={{color: "#70ffaf"}}/></div>;
  }

  return (
    <div className={styles.App}>
      <NavigationBar
        onClick={(item) => nav(`/${item}`)}
        isLoggedIn={authProvider.isAuthenticated}
      />

      <div className={styles.content}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/settings" element={<Root />} />
          <Route path="/login" element={<Auth />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/profile2" element={<UserProfile2 />} />
            <Route path="/logout" element={<Logout />} />
          </Route>
          <Route path="/post/:postID" element={<Post />} />
          <Route path="/authors/:userID" element={<PublicProfile />} />
          <Route path="*" element={<ErrorPage />} />
        </Routes>
      </div>
    </div>
  );
}
