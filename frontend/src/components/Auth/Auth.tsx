import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@mui/material";
import TextField from '@mui/material/TextField';
import { login } from "../../util/auth/login";
import { logout } from "../../util/auth/checkauth";
import styles from './Auth.module.scss';
import { useAuth } from "../../state";
import authService from "../../service/auth";

function Auth() {
   const [isRegister, setIsRegister] = useState(false);
   const [username, setUsername] = useState("");
   const [password, setPassword] = useState("");
   const [name, setName] = useState("");
   const [email, setEmail] = useState("");
   const [confirmPassword, setConfirmPassword] = useState("");
   const [error, setError] = useState("");
   const navigate = useNavigate();
   const authProvider = useAuth();

   const location = useLocation();

   useEffect(() => {
      // Check if user is already logged in, return to prev page
      const from = location.state?.from?.pathname || '/';

      if (authProvider.isAuthenticated) {
         navigate(from);
      }
   }, [authProvider.isAuthenticated, authProvider.loading, navigate, location]);

   const handleSubmit = async (e) => {
      e.preventDefault();
      setError("");

      // Validation
      if (!username || !password || (isRegister && (!name || !email))) {
         setError("Please fill all required fields.");
         return;
      }
      if (isRegister && password !== confirmPassword) {
         setError("Passwords do not match.");
         return;
      }

      if (isRegister) {
         const response = await authService.register({ username, password, email, name });

         if (response) {
            alert("Registration successful! Please log in.");
            setIsRegister(false); // Switch back to login form
          } else {
            setError("Registration failed. Username might already be taken.");
          }

      } else {
         login(username, password)
         .then((response) => {
            authProvider.setIsAuthenticated(true);
            authProvider.setUser(response.user);
            navigate("/");
         })
         .catch((error) => {
            console.log(error);
            setError("Login failed. Please check your credentials.");
         });
      }

      resetFields();
   };

   const resetFields = () => {
      setUsername("");
      setPassword("");
      setName("");
      setEmail("");
      setConfirmPassword("");
   };

   return (
      <div className={styles.auth}>
         <div className={styles.auth__container}>
         <div className={styles.auth__container__header}>
            <h1>{isRegister ? "Register" : "Login"}</h1>
            <p
               className={styles.check}
               onClick={() => setIsRegister(!isRegister)}
            >
               {isRegister ? "Login instead" : "Register instead"}
            </p>
         </div>

         <form className={styles.auth__container__form} onSubmit={handleSubmit}>
            <TextField
               label="Username"
               variant="outlined"
               size="small"
               value={username}
               onChange={(e) => setUsername(e.target.value)}
               required
            />
            {isRegister && (
               <TextField
               label="Name"
               variant="outlined"
               size="small"
               value={name}
               onChange={(e) => setName(e.target.value)}
               required
               />
            )}
            <TextField
               label="Password"
               variant="outlined"
               size="small"
               type="password"
               value={password}
               onChange={(e) => setPassword(e.target.value)}
               required
            />
            {isRegister && (
               <TextField
               label="Confirm Password"
               variant="outlined"
               size="small"
               type="password"
               value={confirmPassword}
               onChange={(e) => setConfirmPassword(e.target.value)}
               required
               />
            )}
            {isRegister && (
               <TextField
               label="Email"
               variant="outlined"
               size="small"
               type="email"
               value={email}
               onChange={(e) => setEmail(e.target.value)}
               required
               />
            )}
            <div className={styles.auth__container__footer}>
               <button type="submit">Submit</button>
               {error && <p className={styles.error}>{error}</p>}
            </div>
         </form>
         </div>
      </div>
   );
}

export function Logout() {
   const navigate = useNavigate();
   const authProvider = useAuth();

   return (
      <div className={styles.auth}>
         <div className={styles.auth__container}>
            <div className={styles.auth__container__header}>
               <h1>Logout</h1>
            </div>
            <div className={styles.auth__container__form}>
               <Button variant="contained" color="primary" onClick={() => {
                  logout().then(() => {
                     navigate("/");
                     authProvider.logout();
                  });
               }}>
                  Logout
               </Button>
            </div>
         </div>
      </div>
   );
}

export default Auth;