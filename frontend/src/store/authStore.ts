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
    error: string | null;
    setAuth: (token: string, user: User) => Promise<void>;
    logout: () => Promise<void>;
    fetchMe: () => Promise<void>;
    loginWithEmail: (email: string, password: string) => Promise<void>;
    registerWithEmail: (email: string, password: string, name: string) => Promise<void>;
}
export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: null,
    isLoading: false,
    error: null,
    setAuth: async (token: string, user: User) => {
        await saveToken(token);
        set({ token, user, error: null });
    },
    logout: async () => {
        await clearToken();
        set({ user: null, token: null, error: null });
    },
    fetchMe: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await api.get('/auth/me');
            set({ user: res.data, isLoading: false });
        } catch {
            await clearToken();
            set({ user: null, token: null, isLoading: false });
        }
    },
    loginWithEmail: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
            const res = await api.post('/auth/email/login', { email, password });
            const { access_token, user } = res.data;
            await saveToken(access_token);
            set({ token: access_token, user, isLoading: false, error: null });
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Login failed';
            set({ isLoading: false, error: message });
            throw new Error(message);
        }
    },
    registerWithEmail: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });
        try {
            const res = await api.post('/auth/register', { email, password, name });
            const { access_token, user } = res.data;
            await saveToken(access_token);
            set({ token: access_token, user, isLoading: false, error: null });
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Registration failed';
            set({ isLoading: false, error: message });
            throw new Error(message);
        }
    },
}));
