/**
 * Tests for the Zustand auth store.
 */
import { act } from '@testing-library/react-native';

// Mock expo-secure-store
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn().mockResolvedValue(null),
  setItemAsync: jest.fn().mockResolvedValue(undefined),
  deleteItemAsync: jest.fn().mockResolvedValue(undefined),
}));

// Mock axios
jest.mock('../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  },
  saveToken: jest.fn().mockResolvedValue(undefined),
  getToken: jest.fn().mockResolvedValue(null),
  clearToken: jest.fn().mockResolvedValue(undefined),
  API_BASE: 'http://localhost:8081',
  WS_BASE: 'ws://localhost:8081',
}));

import { useAuthStore } from '../store/authStore';
import api, { saveToken, clearToken } from '../services/api';

const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  provider: 'google',
  created_at: new Date().toISOString(),
};

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, token: null, isLoading: false });
    jest.clearAllMocks();
  });

  it('should initialize with null user and token', () => {
    const { user, token } = useAuthStore.getState();
    expect(user).toBeNull();
    expect(token).toBeNull();
  });

  it('should set auth state correctly', async () => {
    await act(async () => {
      await useAuthStore.getState().setAuth('test-token', mockUser as any);
    });
    const { user, token } = useAuthStore.getState();
    expect(user).toEqual(mockUser);
    expect(token).toBe('test-token');
    expect(saveToken).toHaveBeenCalledWith('test-token');
  });

  it('should clear auth state on logout', async () => {
    await act(async () => {
      await useAuthStore.getState().setAuth('test-token', mockUser as any);
      await useAuthStore.getState().logout();
    });
    const { user, token } = useAuthStore.getState();
    expect(user).toBeNull();
    expect(token).toBeNull();
    expect(clearToken).toHaveBeenCalled();
  });

  it('should fetch user on fetchMe success', async () => {
    (api.get as jest.Mock).mockResolvedValueOnce({ data: mockUser });
    await act(async () => {
      await useAuthStore.getState().fetchMe();
    });
    expect(useAuthStore.getState().user).toEqual(mockUser);
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it('should clear auth on fetchMe failure', async () => {
    (api.get as jest.Mock).mockRejectedValueOnce(new Error('Unauthorized'));
    await act(async () => {
      await useAuthStore.getState().setAuth('bad-token', mockUser as any);
      await useAuthStore.getState().fetchMe();
    });
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().token).toBeNull();
  });
});
