import axios from "axios";

interface LoginResponse {
   is_authenticated: boolean;
   uuid: string;
   username: string;
   sessionId: string;
}

export async function login(username, password):  Promise<LoginResponse>{
   const response = await axios.post<LoginResponse>("http://localhost:8000/api/login/", {
      username,
      password,
   });

   return response.data;
}