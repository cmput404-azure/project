import { api } from "./config";
import { getHostURL } from "../util/auth/getHostURL";

interface RegisterData {
    username: string;
    password: string;
    email: string;
    name: string;
    githubUsername: string;
}

interface RegisterResponse {
    message: string;
}

class AuthService{
    // register new user
    public async register(data: RegisterData): Promise<RegisterResponse | null> {
        try {
          const host = getHostURL();
          console.log("My host: ", host);
          const response = await api.post<RegisterResponse>("/api/register/", {
            ...data,
            host
          });
          return response.data;
        } catch (error: any) {
          console.error("Error registering user:", error.response?.data || error.message);
          return null;
        }
    }

    
}

const auth = new AuthService();
export default auth;