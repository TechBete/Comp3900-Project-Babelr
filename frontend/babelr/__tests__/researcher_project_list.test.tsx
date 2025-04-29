// __tests__/projects_list.test.tsx

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MainScreen from "../pages/Researcher/project_list"; 
import '@testing-library/jest-dom';

jest.mock("components/role_checker", () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

jest.mock("components/nav_bar_researcher", () => ({
  __esModule: true,
  default: () => <nav>Mocked Navbar</nav>,
}));

jest.mock("components/create_button", () => ({
  __esModule: true,
  default: ({ onClick }: { onClick: () => void }) => (
    <button onClick={onClick}>Open Create Modal</button>
  ),
}));

jest.mock("components/popout_modal", () => ({
  __esModule: true,
  default: ({ children, isOpen }: { children: React.ReactNode, isOpen: boolean }) =>
    isOpen ? <div data-testid="modal">{children}</div> : null,
}));

describe("Researcher Project List Page", () => {
  beforeEach(() => {
    (global.fetch as jest.Mock) = jest.fn();
  });

  it("renders project list page and shows projects", async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        projects_list: [
          { project_name: "Project Alpha", path: "/projects/alpha", status: "draft", creator_name: "John Doe" },
          { project_name: "Project Beta", path: "/projects/beta", status: "in_progress", creator_name: "Jane Smith" },
        ],
      }),
    });

    render(<MainScreen />);

    expect(await screen.findByRole('heading', { name: /your projects/i })).toBeInTheDocument();
    await waitFor(() => {
        expect(screen.getByText("Project Alpha")).toBeInTheDocument();
        expect(screen.getByText("Project Beta")).toBeInTheDocument();
        expect(screen.getByText("Draft")).toBeInTheDocument();
        expect(screen.getByText("In Progress")).toBeInTheDocument();
        expect(screen.getByText("John Doe")).toBeInTheDocument();
        expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    });
  });

  it("opens modal when clicking create button", async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ projects_list: [] }),
    });

    render(<MainScreen />);

    fireEvent.click(screen.getByText("Open Create Modal"));

    expect(await screen.findByTestId("modal")).toBeInTheDocument();
    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
  });

  it("submits new project successfully", async () => {
    (fetch as jest.Mock)
      // First fetch: getProjects (empty)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ projects_list: [] }),
      })
      // Second fetch: createProject
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "Project created!" }),
      })
      // Third fetch: getProjects after creation
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          projects_list: [{ project_name: "Project Gamma", path: "/projects/gamma", status: "draft", creator_name: "John Doe" }],
        }),
      });

    render(<MainScreen />);

    fireEvent.click(screen.getByText("Open Create Modal"));

    const input = await screen.findByLabelText(/project name/i);
    fireEvent.change(input, { target: { value: "Project Gamma" } });

    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(screen.getByText("Project Gamma")).toBeInTheDocument();
    });
  });
});