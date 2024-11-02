import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@mui/material";
import TextField from "@mui/material/TextField";
import { login } from "../../util/auth/login";
import { logout } from "../../util/auth/checkauth";
import styles from "./Auth.module.scss";
import { useAuth } from "../../state";
import authService from "../../service/auth";
import styled from "@mui/material/styles/styled";
import { InputAdornment } from "@mui/material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { Email } from "@mui/icons-material";
import { GitHub } from "@mui/icons-material";
import Lock from "@mui/icons-material/Lock";
import { IconButton } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";

const StyledTextField = styled(TextField)({
  "& label": {
    color: "#ffffff !important",
  },

  "& input": {
    color: "white !important",
    backgroundColor: "#2b2b2b", // lighter gray background inside the input
    padding: "10px", // Optional: to add some padding around the text
    borderRadius: "5px", // Optional: to add rounded corners
  },
  "& textarea": {
    color: "white !important",
  },

  "& .MuiOutlinedInput-root": {
    "& fieldset": {
      border: "none",
      boxShadow: "0 4px 7px rgba(0, 0, 0, 0.45)",
    },
    "&:hover fieldset": {
      border: "1px solid",
      borderColor: "white !important",
    },
    "&.Mui-focused fieldset": {
      border: "1px solid",
      borderColor: "#70ffaf !important",
    },
    // style the slotPropr input icon color
    "& .MuiSvgIcon-root": {
      color: "#fff",
    },
    // style the slotProps end adornment icon button
    "& .MuiIconButton-root": {
      color: "#fff",
      backgroundColor: "#2b2b2b",
      width: "40px",
      height: "40px",
    },
  },

  "& .MuiFormHelperText-root": {
    color: "#ffffff",
    "&.Mui-error": {
      color: "#dc3545",
    },
  },
});

function Auth() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [githubUsername, setGithubUsername] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const authProvider = useAuth();

  const location = useLocation();

  useEffect(() => {
    // Check if user is already logged in, return to prev page
    const from = location.state?.from?.pathname || "/";

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
      const response = await authService.register({
        username,
        password,
        email,
        name,
        githubUsername,
      });

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
          setError(error.response.data.message);
        });
    }

    resetFields();
  };

  const resetFields = () => {
    setUsername("");
    setPassword("");
    setName("");
    setGithubUsername("");
    setEmail("");
    setConfirmPassword("");
  };

  const handleClickShowPassword = (isConfirm) => {
    if (isConfirm) {
      setShowPasswordConfirm(!showPasswordConfirm);
    } else {
      setShowPassword(!showPassword);
    }
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const handleMouseUpPassword = (event) => {
    event.preventDefault();
  };

  return (
    <div className={styles.auth}>
      <div className={styles.auth__container}>
        <div className={styles.auth__container__header}>
          <h1>{isRegister ? "Register" : "Login"}</h1>
        </div>

        <form className={styles.auth__container__form} onSubmit={handleSubmit}>
          <StyledTextField
            label="Username"
            variant="outlined"
            size="small"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircle />
                  </InputAdornment>
                ),
              },
            }}
          />
          {isRegister && (
            <StyledTextField
              label="Name"
              variant="outlined"
              size="small"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <AccountCircle />
                    </InputAdornment>
                  ),
                },
              }}
            />
          )}
          {isRegister && (
            <StyledTextField
              label="Email"
              variant="outlined"
              size="small"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email />
                    </InputAdornment>
                  ),
                },
              }}
            />
          )}
          {isRegister && (
            <StyledTextField
              label="GitHub Username"
              variant="outlined"
              size="small"
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <GitHub />
                    </InputAdornment>
                  ),
                },
              }}
            />
          )}
          <StyledTextField
            label="Password"
            variant="outlined"
            size="small"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={
                        showPassword
                          ? "hide the password"
                          : "display the password"
                      }
                      onClick={() => handleClickShowPassword(false)}
                      onMouseDown={handleMouseDownPassword}
                      onMouseUp={handleMouseUpPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />
          {isRegister && (
            <StyledTextField
              label="Confirm Password"
              variant="outlined"
              size="small"
              type={showPasswordConfirm ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label={
                          showPassword
                            ? "hide the password"
                            : "display the password"
                        }
                        onClick={() => handleClickShowPassword(true)}
                        onMouseDown={handleMouseDownPassword}
                        onMouseUp={handleMouseUpPassword}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
          )}
          <div className={styles.auth__container__footer}>
            <button type="submit">Submit</button>
            {error && <p className={styles.error}>{error}</p>}
          </div>
        </form>
        <section className={styles.auth__container__footer}>
          <p className={styles.auth__account__or__not}>
            {isRegister ? "Already have an account?" : "Don't have an account?"}
          </p>
          <p
            className={styles.check}
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? "Login instead" : "Register instead"}
          </p>
        </section>
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
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              logout().then(() => {
                navigate("/");
                authProvider.logout();
              });
            }}
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}

export default Auth;
