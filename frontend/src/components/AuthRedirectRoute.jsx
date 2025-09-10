import axios from "axios";
import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { API_BASE_URL } from "../config";

const AuthRedirectRoute = ({ children }) => {
  const [valid, setValid] = useState(null);
  const token = localStorage.getItem("token");
  const { pathname } = useLocation();
  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setValid(false);
        return;
      }
      try {
        await axios.get(`${API_BASE_URL}/api/user/authorise`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setValid(true);
      } catch (e) {
        console.error(
          "Unable to verify token, Please log in again",
          e.response?.status
        );
        setValid(false);
      }
    };
    verify();
  }, [token]);

  if (valid === null) {
    // Doesn't render anything while waiting for API response.
    return null;
  }

  if (valid === true) {
    // If token is valid and user is on login/signup, redirect to home
    if (pathname === "/login" || pathname === "/signup") {
      return <Navigate to="/" replace />;
    }
  }

  if (valid === false) {
    // If current route is not login/signup -> then redirect to landing page
    if (pathname !== "/login" && pathname !== "/signup") {
      console.log("Token not found, redirecting to landing page");
      return <Navigate to="/landing" replace />;
    }
  }

  return children;
};

export default AuthRedirectRoute;
