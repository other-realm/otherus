/**
 * Tests for the API service token helpers.
 */

jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

import * as SecureStore from 'expo-secure-store';

// We test the token helpers by importing them after mocking
describe('Token helpers (native)', () => {
  // Simulate native platform
  jest.mock('react-native', () => ({
    Platform: { OS: 'ios' },
  }));

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('saveToken calls SecureStore.setItemAsync', async () => {
    (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);
    const { saveToken } = require('../services/api');
    await saveToken('my-token');
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith('access_token', 'my-token');
  });

  it('getToken calls SecureStore.getItemAsync', async () => {
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('stored-token');
    const { getToken } = require('../services/api');
    const token = await getToken();
    expect(token).toBe('stored-token');
  });

  it('clearToken calls SecureStore.deleteItemAsync', async () => {
    (SecureStore.deleteItemAsync as jest.Mock).mockResolvedValue(undefined);
    const { clearToken } = require('../services/api');
    await clearToken();
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith('access_token');
  });
});

describe('API base URL', () => {
  it('should have correct API_BASE', () => {
    const { API_BASE } = require('../services/api');
    expect(typeof API_BASE).toBe('string');
    expect(API_BASE).toMatch(/^http/);
  });

  it('WS_BASE should use ws protocol', () => {
    const { WS_BASE } = require('../services/api');
    expect(WS_BASE).toMatch(/^ws/);
  });
});
