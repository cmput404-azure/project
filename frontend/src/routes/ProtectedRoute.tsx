import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

import { CircularProgress } from "@mui/material";
import { useAuth } from "../state";

export default function ProtectedRoute() {
  const authProvider = useAuth();
  const [loaded, setLoaded] = useState(false);
  const location = useLocation();

   useEffect(() => {
      if (!authProvider.loading) {
         setLoaded(true);
      }
   }, [authProvider.loading]);

   if (!loaded || authProvider.loading) {
      return <div className={"loading"}><CircularProgress sx={{color: "#70ffaf"}}/></div>;
   }

   if (loaded && !authProvider.isAuthenticated) {
      const redirect = location.pathname === "/logout" ? { pathname: "/" } : location;
      return <Navigate to="/login" state={{ from: redirect }} replace />;
   }

  return <Outlet />;
}