import { render, screen } from "@testing-library/react";
import Home_Listener from "../pages/Listener/home_listener";
import '@testing-library/jest-dom';

// Mock next/router (even though this page may not use it directly — good habit)
jest.mock("next/router", () => ({
  __esModule: true,
  useRouter: () => ({ push: jest.fn() }),
}));

// Mock RoleCheck to just render children
jest.mock("components/role_checker", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Mock Navbar_Listener
jest.mock("components/nav_bar_listener", () => {
  return {
    __esModule: true,
    default: () => <nav>Mocked Navbar</nav>,
  };
});

describe("Home Listener Page", () => {
  it("renders correctly", () => {
    render(<Home_Listener />);

    // Check if mocked navbar appears
    expect(screen.getByText(/mocked navbar/i)).toBeInTheDocument();

    // Check if heading appears
    expect(screen.getByRole('heading', { name: /user register/i })).toBeInTheDocument();

    // Check if instruction text appears
    expect(screen.getByText(/click the start rating button to begin/i)).toBeInTheDocument();

    // Check if link exists
    const startLink = screen.getByRole('link', { name: /start rating/i });
    expect(startLink).toBeInTheDocument();
    expect(startLink).toHaveAttribute('href', '/Listener/evaluation');
  });
});