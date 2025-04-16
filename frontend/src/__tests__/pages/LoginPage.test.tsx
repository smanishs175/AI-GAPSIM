// @ts-nocheck
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '@/pages/LoginPage';
import { useAuthStore } from '@/store/authStore';

// Mock the auth store
jest.mock('@/store/authStore', () => ({
  useAuthStore: jest.fn()
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('LoginPage', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup default mock implementation for useAuthStore
    (useAuthStore as jest.Mock).mockReturnValue({
      login: jest.fn(),
      isAuthenticated: false,
      isLoading: false,
      error: null,
      clearError: jest.fn()
    });
  });

  it('renders the login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check if the title is rendered
    expect(screen.getByText('AI-GAPSIM')).toBeInTheDocument();

    // Check if form elements are rendered
    expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign in/i })).toBeInTheDocument();

    // Check if the signup link is rendered
    expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Sign up/i })).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const mockLogin = jest.fn();
    (useAuthStore as jest.Mock).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      clearError: jest.fn()
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Email address/i), {
      target: { value: 'test@example.com' }
    });

    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Sign in/i }));

    // Check if login was called with correct arguments
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
  });

  it('shows loading state during authentication', () => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: jest.fn(),
      isAuthenticated: false,
      isLoading: true,
      error: null,
      clearError: jest.fn()
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check if loading state is shown
    expect(screen.getByRole('button', { name: /Signing in/i })).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows error message when authentication fails', () => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: jest.fn(),
      isAuthenticated: false,
      isLoading: false,
      error: 'Invalid credentials',
      clearError: jest.fn()
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check if error message is shown
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
  });

  it('redirects to dashboard when already authenticated', () => {
    (useAuthStore as jest.Mock).mockReturnValue({
      login: jest.fn(),
      isAuthenticated: true,
      isLoading: false,
      error: null,
      clearError: jest.fn()
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Check if navigate was called with correct path
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('clears error when component unmounts', () => {
    const mockClearError = jest.fn();
    (useAuthStore as jest.Mock).mockReturnValue({
      login: jest.fn(),
      isAuthenticated: false,
      isLoading: false,
      error: 'Some error',
      clearError: mockClearError
    });

    const { unmount } = render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // Unmount component
    unmount();

    // Check if clearError was called
    expect(mockClearError).toHaveBeenCalled();
  });
});
