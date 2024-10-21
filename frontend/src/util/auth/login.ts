import { User } from "../../models/models";
import { api } from "../../service/config";

interface LoginResponse {
   is_authenticated: boolean;
   user: User;
}

export async function login(username, password):  Promise<LoginResponse>{
   const response = await api.post<LoginResponse>("/api/login/", {
      username,
      password,
   });

   return response.data;
}