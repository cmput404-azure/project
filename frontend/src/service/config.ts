import axios from "axios";
import getCsrfToken from "../util/auth/getCSRF";

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

const csrfToken = getCsrfToken();

export const api = axios.create({
   baseURL: 'http://localhost:8000',
   timeout: 1000,
   headers: {
      "x-csrftoken": csrfToken,
   },
});