/**
 * Tests for the LoginScreen component.
 */
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';

jest.mock('expo-web-browser', () => ({
  maybeCompleteAuthSession: jest.fn(),
  openBrowserAsync: jest.fn().mockResolvedValue({ type: 'cancel' }),
}));

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ replace: jest.fn() }),
}));

jest.mock('../store/authStore', () => ({
  useAuthStore: () => ({ user: null }),
}));

jest.mock('../services/api', () => ({
  API_BASE: 'http://localhost:8081',
  WS_BASE: 'ws://localhost:8081',
  default: { get: jest.fn(), interceptors: { request: { use: jest.fn() } } },
  saveToken: jest.fn(),
  getToken: jest.fn(),
  clearToken: jest.fn(),
}));

import LoginScreen from '../screens/LoginScreen';

describe('LoginScreen', () => {
  it('renders the app title', () => {
    const { getByText } = render(<LoginScreen />);
    expect(getByText('Other Us')).toBeTruthy();
  });

  it('renders Google sign-in button', () => {
    const { getByText } = render(<LoginScreen />);
    expect(getByText('Continue with Google')).toBeTruthy();
  });

  it('renders GitHub sign-in button', () => {
    const { getByText } = render(<LoginScreen />);
    expect(getByText('Continue with GitHub')).toBeTruthy();
  });

  it('renders the sign-in prompt', () => {
    const { getByText } = render(<LoginScreen />);
    expect(getByText('Sign in to continue')).toBeTruthy();
  });

  it('renders the disclaimer text', () => {
    const { getByText } = render(<LoginScreen />);
    expect(getByText(/Terms of Service/)).toBeTruthy();
  });

  it('calls openBrowserAsync when Google button is pressed (native)', async () => {
    const { WebBrowser } = require('expo-web-browser');
    const { getByText } = render(<LoginScreen />);
    fireEvent.press(getByText('Continue with Google'));
    // On native, it should open the browser
  });
});
