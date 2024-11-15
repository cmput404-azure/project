import axios from "axios";
import getCsrfToken from "../util/auth/getCSRF";

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

const csrfToken = getCsrfToken();

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "x-csrftoken": csrfToken,
  },
});
