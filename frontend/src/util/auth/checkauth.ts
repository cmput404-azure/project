import { User } from "../../models/models";
import { api } from "../../service/config";
import axios from "axios";

interface CheckAuthResponse {
   is_authenticated: boolean;
   user: User;
}

interface LogoutResponse {
   status: string;
}

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

export async function checkAuth(): Promise<CheckAuthResponse> {
   try {
      const res = await api.get<CheckAuthResponse>("/api/check_auth/");
      return res.data;
   } 
   catch (error) {
      console.error("Error fetching the author data", error);
   }
}

export async function logout(): Promise<LogoutResponse> {
   try {
      // clear the cookies
      const res = await api.get<LogoutResponse>("/api/logout/");
      return res.data;
   }
   catch (error) {
      console.error("Error fetching the author data", error);
   }
}