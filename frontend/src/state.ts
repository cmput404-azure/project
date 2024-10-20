import {User} from "./models/models";
import {create} from 'zustand';

interface AuthState {
   isAuthenticated: boolean;
   setIsAuthenticated: (isAuthenticated: boolean) => void;
   user: User | null;
   setUser: (user: User) => void;
   login: (isAuthenticated: boolean, user: User) => void;
   logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
   isAuthenticated: false,
   setIsAuthenticated: (isAuthenticated: boolean) => set({ isAuthenticated }),
   user: null,
   setUser: (user: User) => set({ user }),
   login: (isAuthenticated: boolean, user: User) => set({ isAuthenticated, user }),
   logout: () => set({ isAuthenticated: false, user: null }),
}));