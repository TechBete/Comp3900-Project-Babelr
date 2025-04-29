import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RegisterResearcher from "../pages/Auth/register_researcher"; 
// import '@testing-library/jest-dom/extend-expect';
import { useRouter } from 'next/router';
import '@testing-library/jest-dom'


jest.mock('next/router', () => ({
    useRouter: jest.fn(),
  }));

describe('Register Researcher Page', () => {
  const pushMock = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
    });
    pushMock.mockReset();
  });

  it('renders the register page', () => {
    render(<RegisterResearcher />);
    expect(screen.getByRole('heading', { name: /researcher register/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });  

  it('shows error when passwords do not match', () => {
    render(<RegisterResearcher />);

    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password456' } });
    fireEvent.blur(screen.getByLabelText(/confirm password/i));

    expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument();
  });

  it('submits form and redirects on successful registration', async () => {
    global.fetch = jest.fn().mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    render(<RegisterResearcher />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } });
    fireEvent.blur(screen.getByLabelText(/confirm password/i));

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Auth/login");
    });
  });

  it('shows server error on failed registration', async () => {
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: "Email already exists" }),
    });

    render(<RegisterResearcher />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'duplicate@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } });
    fireEvent.blur(screen.getByLabelText(/confirm password/i));

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
    });
  });

  it('shows network error if fetch throws', async () => {
    global.fetch = jest.fn().mockRejectedValueOnce(new Error('Network error'));

    render(<RegisterResearcher />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'password123' } });
    fireEvent.blur(screen.getByLabelText(/confirm password/i));

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/network error: fetch request failed/i)).toBeInTheDocument();
    });
  });
});