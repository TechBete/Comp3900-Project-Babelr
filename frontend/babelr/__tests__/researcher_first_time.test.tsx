import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import First_time from "../pages/Researcher/first_time_researcher"; 
import router from "next/router";  // default import
import '@testing-library/jest-dom';

jest.mock("next/router", () => ({
  __esModule: true,
  default: {
    push: jest.fn(),
  },
}));

jest.mock("components/role_checker", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

describe("Researcher First Time Page", () => {

  beforeEach(() => {
    (router.push as jest.Mock).mockReset();
  });

  it("renders the first time researcher page", () => {
    render(<First_time />);
    expect(screen.getByRole('heading', { name: /welcome to babelr/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/organisation/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
  });

  it("submits form successfully and redirects", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    render(<First_time />);

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/organisation/i), { target: { value: 'UNSW' } });

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(router.push).toHaveBeenCalledWith('project_list');
    });
  });

});