import { User } from "../../models/models";
import axios from "axios";

interface LoginResponse {
   is_authenticated: boolean;
   user: User;
}

export async function login(username, password):  Promise<LoginResponse>{
   const response = await axios.post<LoginResponse>("http://localhost:8000/api/login/", {
      username,
      password,
   });

   return response.data;
}