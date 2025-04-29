import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ProfilePage from "../pages/Researcher/profile"; // Adjust if the path is different
import '@testing-library/jest-dom';

// Mock RoleCheck (so it doesn't fetch anything)
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

// Mock fetch globally
beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});
describe("Listener Profile Page", () => {
    it("renders profile page and user data correctly", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          Uuid: "123",
          "First Name": "John",
          "Last Name": "Doe",
          Email: "john@example.com",
          Password: "********",
          "Date of Birth": "1990-01-01",
          Gender: "male",
          Country: "Australia",
          Education: "University",
          Organisation: "UNSW",
        }),
      });
  
      render(<ProfilePage />);
  
      // Wait for data to load
      expect(await screen.findByText("Profile")).toBeInTheDocument();
  
      // Basic profile fields
      expect(await screen.findByText("john@example.com")).toBeInTheDocument();
      expect(await screen.findByText("John")).toBeInTheDocument();
      expect(await screen.findByText("Doe")).toBeInTheDocument();
      expect(await screen.findByText("Australia")).toBeInTheDocument();
      expect(await screen.findByText("University")).toBeInTheDocument();
      expect(await screen.findByText("UNSW")).toBeInTheDocument();
    });
  
    it("opens password dialog when clicking Update Password", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            Uuid: "123",
            "First Name": "John",
            "Last Name": "Doe",
            Email: "john@example.com",
            Password: "********",
            "Date of Birth": "1990-01-01",
            Gender: "male",
            Country: "Australia",
            Education: "University",
            Organisation: "UNSW",
          }),
      });
  
      render(<ProfilePage />);
  
      // Wait for profile to load using something that loads after fetch
      await screen.findByText("john@example.com");
  
      // Open password edit
      fireEvent.click(screen.getByRole('button', { name: /update password/i }));
  
      // Password fields appear
      expect(await screen.findByLabelText(/new password/i)).toBeInTheDocument();
      expect(await screen.findByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it("opens personal info dialog when clicking Edit Info", async () => {
        (fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            Uuid: "123",
            "First Name": "John",
            "Last Name": "Doe",
            Email: "john@example.com",
            Password: "********",
            "Date of Birth": "1990-01-01",
            Gender: "male",
            Country: "Australia",
            Education: "University",
            Organisation: "UNSW",
          }),
        });
    
        render(<ProfilePage />);
    
        await screen.findByText("john@example.com");
    
        // Open personal info edit
        fireEvent.click(screen.getByRole('button', { name: /edit info/i }));
    
        // Fields appear
        expect(await screen.findByLabelText(/first name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/country/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/education/i)).toBeInTheDocument();
      });
});