import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

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
      return <div>Loading...</div>;
   }

   if (loaded && !authProvider.isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
   }

  return <Outlet />;
}