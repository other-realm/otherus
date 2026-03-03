/**
 * Tests for the SettingsScreen component — focusing on account deletion flow.
 */
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ replace: jest.fn(), goBack: jest.fn() }),
}));

const mockLogout = jest.fn();
const mockUser = {
  id: 'user-123',
  name: 'Test User',
  email: 'test@example.com',
  provider: 'google',
  ntfy_topic: 'other-us-abc123',
  is_admin: false,
};

jest.mock('../store/authStore', () => ({
  useAuthStore: () => ({ user: mockUser, logout: mockLogout }),
}));

jest.mock('../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    put: jest.fn().mockResolvedValue({ data: { ntfy_topic: 'updated-topic' } }),
    delete: jest.fn().mockResolvedValue({}),
    interceptors: { request: { use: jest.fn() } },
  },
  saveToken: jest.fn(),
  getToken: jest.fn(),
  clearToken: jest.fn(),
  API_BASE: 'http://localhost:8081',
  WS_BASE: 'ws://localhost:8081',
}));

import SettingsScreen from '../screens/SettingsScreen';

describe('SettingsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(Alert, 'alert');
  });

  it('renders user name and email', () => {
    const { getByText } = render(<SettingsScreen />);
    expect(getByText('Test User')).toBeTruthy();
    expect(getByText('test@example.com')).toBeTruthy();
  });

  it('renders sign out button', () => {
    const { getByText } = render(<SettingsScreen />);
    expect(getByText('Sign Out')).toBeTruthy();
  });

  it('renders delete account button', () => {
    const { getByText } = render(<SettingsScreen />);
    expect(getByText('Delete My Account')).toBeTruthy();
  });

  it('shows confirmation alert when delete button is pressed', () => {
    const { getByText } = render(<SettingsScreen />);
    fireEvent.press(getByText('Delete My Account'));
    expect(Alert.alert).toHaveBeenCalledWith(
      expect.stringContaining('Delete Account'),
      expect.stringContaining('permanent'),
      expect.any(Array)
    );
  });

  it('calls logout when sign out is pressed', async () => {
    const { getByText } = render(<SettingsScreen />);
    fireEvent.press(getByText('Sign Out'));
    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('shows ntfy topic input with current value', () => {
    const { getByDisplayValue } = render(<SettingsScreen />);
    expect(getByDisplayValue('other-us-abc123')).toBeTruthy();
  });

  it('saves ntfy topic when save button is pressed', async () => {
    const api = require('../services/api').default;
    const { getByText } = render(<SettingsScreen />);
    fireEvent.press(getByText('Save Notification Topic'));
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/users/me/ntfy', expect.any(Object));
    });
  });
});
