import axios from "axios";
import getCsrfToken from "../util/auth/getCSRF";

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 10000,
});

// Referenced ChatGPT "csrf token upon logging in is different than the ones sent in requests" on Nov 11, 2024
// This function thus ensures the csrf token is updated dynamically for each request
api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    config.headers["X-CSRFToken"] = csrfToken;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});
