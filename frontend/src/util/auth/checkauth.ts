import axios from "axios";

interface CheckAuthResponse {
   is_authenticated: boolean;
   username: string;
   uuid: string;
}

interface LogoutResponse {
   status: string;
}

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

export async function checkAuth(): Promise<CheckAuthResponse> {
   

   try {
      const res = await axios.get<CheckAuthResponse>("http://localhost:8000/api/check_auth/");
      return res.data;
   } 
   catch (error) {
      console.error("Error fetching the author data", error);
   }
}

export async function logout(): Promise<LogoutResponse> {
   try {
      // clear the cookies
      const res = await axios.get<LogoutResponse>("http://localhost:8000/api/logout/");
      return res.data;
   }
   catch (error) {
      console.error("Error fetching the author data", error);
   }
}