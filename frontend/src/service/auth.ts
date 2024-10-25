import { api } from "./config";

interface RegisterData {
    username: string;
    password: string;
    email: string;
    name: string;
}

interface RegisterResponse {
    message: string;
}

class AuthService{
    // register new user
    public async register(data: RegisterData): Promise<RegisterResponse | null> {
        try {
          const response = await api.post<RegisterResponse>("/api/register/", data);
          return response.data;
        } catch (error: any) {
          console.error("Error registering user:", error.response?.data || error.message);
          return null;
        }
    }
}

const auth = new AuthService();
export default auth;