// @ts-nocheck
import { act } from 'react-dom/test-utils';
import { useAuthStore } from '@/store/authStore';

// Mock fetch
global.fetch = jest.fn();

describe('Auth Store', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Reset store state
    act(() => {
      useAuthStore.setState({
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      });
    });
  });

  it('should initialize with default values', () => {
    const state = useAuthStore.getState();

    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should update state during login process', async () => {
    // Mock successful login response
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/api/auth/login')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token'
          })
        });
      } else if (url.includes('/api/auth/me')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            full_name: 'Test User'
          })
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    // Start login process
    const { login } = useAuthStore.getState();
    await act(async () => {
      await login('test@example.com', 'password123');
    });

    // Check state after login
    const state = useAuthStore.getState();
    expect(state.isLoading).toBe(false);
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe('test-access-token');
    expect(state.refreshToken).toBe('test-refresh-token');
    expect(state.user).toEqual({
      id: 1,
      email: 'test@example.com',
      username: 'testuser',
      full_name: 'Test User'
    });
    expect(state.error).toBeNull();

    // Verify fetch was called correctly
    expect(global.fetch).toHaveBeenCalledTimes(2);
    expect(global.fetch).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/auth/login`,
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        }
      })
    );
  });

  it('should handle login errors', async () => {
    // Mock failed login response
    (global.fetch as jest.Mock).mockImplementation(() => {
      return Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: 'Invalid credentials'
        })
      });
    });

    // Start login process
    const { login } = useAuthStore.getState();
    await act(async () => {
      await login('test@example.com', 'wrong-password');
    });

    // Check state after failed login
    const state = useAuthStore.getState();
    expect(state.isLoading).toBe(false);
    expect(state.isAuthenticated).toBe(false);
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
    expect(state.error).toBe('Invalid credentials');

    // Verify fetch was called correctly
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('should clear user data on logout', async () => {
    // Set initial authenticated state
    act(() => {
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', username: 'testuser', full_name: 'Test User' },
        token: 'test-token',
        refreshToken: 'test-refresh-token',
        isAuthenticated: true
      });
    });

    // Perform logout
    const { logout } = useAuthStore.getState();
    act(() => {
      logout();
    });

    // Check state after logout
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should clear error when requested', async () => {
    // Set initial state with error
    act(() => {
      useAuthStore.setState({
        error: 'Test error'
      });
    });

    // Clear error
    const { clearError } = useAuthStore.getState();
    act(() => {
      clearError();
    });

    // Check state after clearing error
    const state = useAuthStore.getState();
    expect(state.error).toBeNull();
  });
});
