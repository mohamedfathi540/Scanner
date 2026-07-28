import { create } from 'zustand';

interface AuthState {
    // State
    token: string | null;
    userEmail: string | null;
    isAuthenticated: boolean;

    // Actions
    login: (token: string, email: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
    token: 'local-token',
    userEmail: 'local@daftar.com',
    isAuthenticated: true,

    login: (token, email) =>
        set({ token, userEmail: email, isAuthenticated: true }),

    logout: () =>
        set({ token: 'local-token', userEmail: 'local@daftar.com', isAuthenticated: true }),
}));
