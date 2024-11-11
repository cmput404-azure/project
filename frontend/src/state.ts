import { User } from './models/models';
import { checkAuth } from './util/auth/checkauth';
import { create } from 'zustand';

interface AuthState {
   isAuthenticated: boolean;
   user: User | null;
   loading: boolean; 
   setIsAuthenticated: (isAuthenticated: boolean) => void;
   setUser: (user: User | null) => void;
   logout: () => void;
   initializeAuth: () => void;
 }
 
 export const useAuth = create<AuthState>((set) => {
   const initializeAuth = async () => {
      set({ loading: true }); 
      try {
         const data = await checkAuth();
         set({
            isAuthenticated: data?.is_authenticated || false,
            user: data?.user || null,
            loading: false, 
         });
      } catch (error) {
         console.error('Failed to initialize authentication', error);
         set({ isAuthenticated: false, user: null, loading: false });
      }
   };
 
   initializeAuth();
 
   return {
      isAuthenticated: false,
      user: null,
      loading: false, 
      setIsAuthenticated: (isAuthenticated: boolean) => set({ isAuthenticated }),
      setUser: (user: User | null) => set({ user }),
      logout: () => set({ isAuthenticated: false, user: null }),
      initializeAuth,
   };
});