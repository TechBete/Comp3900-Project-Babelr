import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Page from '../pages/Auth/login'
import { useRouter } from 'next/router';

jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));
 
describe('Login Page', () => {
  const pushMock = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
    })
    pushMock.mockReset();
  })


  it('renders the login page', () => {
    render(<Page />)
    expect(screen.getByRole('heading', { name: /babelr login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
 
  })

  it('fills form fields', () => {
    render(<Page />);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  it('handles successful login and redirects a first time researcher', async () => {
    // Mock successful login response
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })  // login
      .mockResolvedValueOnce({ json: async () => ({ role: "researcher", first_time: true }) }); // getRoleFromID

    render(<Page />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Researcher/first_time_researcher");
    });
  });

  it('handles successful login and redirects a previously logged in researcher', async () => {
    // Mock successful login response
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })  // login
      .mockResolvedValueOnce({ json: async () => ({ role: "researcher", first_time: false }) }); // getRoleFromID

    render(<Page />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Researcher/project_list");
    });
  });

  it('handles successful login and redirects a previously logged in user', async () => {
    // Mock successful login response
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })  // login
      .mockResolvedValueOnce({ json: async () => ({ role: "listener", first_time: false }) }); // getRoleFromID

    render(<Page />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Listener/home_listener");
    });
  });

  it('handles successful login and redirects a first time user', async () => {
    // Mock successful login response
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })  // login
      .mockResolvedValueOnce({ json: async () => ({ role: "listener", first_time: true }) }); // getRoleFromID

    render(<Page />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Listener/first_time_listener");
    });
  });

  it('handles login failure', async () => {
    // Mock failed login response
    global.fetch = jest.fn()
      .mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: "Invalid credentials" }),
      });

    render(<Page />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'wrong@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpassword' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('switches sign up option', () => {
    render(<Page />);
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '/Auth/register_researcher' } });

    expect(select).toHaveValue('/Auth/register_researcher');
  });
})