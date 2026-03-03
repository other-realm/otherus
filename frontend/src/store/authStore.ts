import { create } from 'zustand';
import api, { saveToken, clearToken } from '../services/api';
export interface User {
    id: string;
    email: string;
    name: string;
    avatar_url?: string;
    provider: string;
    created_at: string;
    ntfy_topic?: string;
    is_admin?: boolean;
    profile?: boolean;
}
interface AuthState {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    setAuth: (token: string, user: User) => Promise<void>;
    logout: () => Promise<void>;
    fetchMe: () => Promise<void>;
}
export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: null,
    isLoading: false,
    setAuth: async (token: string, user: User) => {
        await saveToken(token);
        set({ token, user });
    },
    logout: async () => {
        await clearToken();
        set({ user: null, token: null });
    },
    fetchMe: async () => {
        set({ isLoading: true });
        try {
            const res = await api.get('/auth/me');
            set({ user: res.data, isLoading: false });
        } catch {
            await clearToken();
            set({ user: null, token: null, isLoading: false });
        }
    },
}));
