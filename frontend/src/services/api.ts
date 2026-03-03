import axios from 'axios';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
export const API_BASE = Platform.OS === 'web'
    ? 'http://localhost:8081'
    : 'http://10.0.2.2:8081'; // Android emulator loopback
export const WS_BASE = API_BASE.replace('http', 'ws');
const api = axios.create({
    baseURL: API_BASE,
    timeout: 15000,
});
// Attach JWT token to every request
api.interceptors.request.use(async (config) => {
    let token: string | null = null;
    if (Platform.OS === 'web') {
        token = localStorage.getItem('access_token');
    } else {
        token = await SecureStore.getItemAsync('access_token');
    }
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
export default api;
// ── Token helpers ──────────────────────────────────────────────────────────────
export async function saveToken(token: string): Promise<void> {
    if (Platform.OS === 'web') {
        localStorage.setItem('access_token', token);
    } else {
        await SecureStore.setItemAsync('access_token', token);
    }
}
export async function getToken(): Promise<string | null> {
    if (Platform.OS === 'web') {
        return localStorage.getItem('access_token');
    }
    return SecureStore.getItemAsync('access_token');
}
export async function clearToken(): Promise<void> {
    if (Platform.OS === 'web') {
        localStorage.removeItem('access_token');
    } else {
        await SecureStore.deleteItemAsync('access_token');
    }
}