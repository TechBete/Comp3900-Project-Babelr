import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import First_time from "../pages/Listener/first_time_listener"; 
import { useRouter } from "next/router";
import '@testing-library/jest-dom'

jest.mock("next/router", () => ({
    useRouter: jest.fn(),
}));
  
jest.mock("components/role_checker", () => {
    return {
      __esModule: true,
      default: ({ children }: { children: React.ReactNode }) => <>{children}</>
    };
});

jest.mock("components/date_picker", () => {
    return {
      __esModule: true,
      default: ({}) => <input type="date" name="date_of_birth" id="date_of_birth" />
    };
  });
;

describe("First Time Listener Page", () => {
  const pushMock = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
    });
    pushMock.mockReset();
  });

  it("renders the first time listener page", () => {
    render(<First_time />);
    expect(screen.getByRole('heading', { name: /welcome to babelr/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/gender/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/country of residence/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/highest level of completed education/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
  });

  
  it("fills form fields", () => {
    render(<First_time />);

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/gender/i), { target: { value: 'male' } });
    fireEvent.change(screen.getByLabelText(/date of birth/i), { target: { value: '2000-01-01' } });
    fireEvent.change(screen.getByLabelText(/country of residence/i), { target: { value: 'Australia' } });
    fireEvent.change(screen.getByLabelText(/highest level of completed education/i), { target: { value: 'University' } });

    expect(screen.getByLabelText(/first name/i)).toHaveValue('John');
    expect(screen.getByLabelText(/last name/i)).toHaveValue('Doe');
    expect(screen.getByLabelText(/gender/i)).toHaveValue('male');
    expect(screen.getByLabelText(/date of birth/i)).toHaveValue('2000-01-01');
    expect(screen.getByLabelText(/country of residence/i)).toHaveValue('Australia');
    expect(screen.getByLabelText(/highest level of completed education/i)).toHaveValue('University');
  });

  it("submits form successfully and redirects", async () => {
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    render(<First_time />);

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/gender/i), { target: { value: 'male' } });
    fireEvent.change(screen.getByLabelText(/date of birth/i), { target: { value: '2000-01-01' } });
    fireEvent.change(screen.getByLabelText(/country of residence/i), { target: { value: 'Australia' } });
    fireEvent.change(screen.getByLabelText(/highest level of completed education/i), { target: { value: 'University' } });

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith('first_time_listener_lg');
    });
  });
});