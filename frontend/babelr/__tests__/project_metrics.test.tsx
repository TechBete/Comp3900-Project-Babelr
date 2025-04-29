import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MetricsPage from "pages/app/audioData/[userId]/[projectName]/metrics"; 
import { useRouter } from "next/router";
import '@testing-library/jest-dom';

jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));

jest.mock("components/nav_bar_researcher", () => ({
    __esModule: true,
    default: () => <nav>Mocked Navbar</nav>,
  }));
  
  jest.mock("components/project_sidebar", () => ({
    __esModule: true,
    default: ({ project_name }: { project_name: string }) => <aside>Sidebar for {project_name}</aside>,
  }));

  jest.mock("components/role_checker", () => ({
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  }));

describe("Researcher Metrics Page", () => {
    beforeEach(() => {
      (global.fetch as jest.Mock) = jest.fn();
      (useRouter as jest.Mock).mockReturnValue({ query: { projectName: "TestProject" } });
    });
  
    it("renders metrics dashboard with metrics", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          metrics: {
            "Clarity": {
              min: 1,
              max: 5,
              "minimum label": "Unclear",
              "maximum label": "Clear",
              description: "How clear the audio sounds",
            }
          }
        }),
      });
  
      render(<MetricsPage />);
  
      expect(await screen.findByRole('heading', { name: /metrics dashboard/i })).toBeInTheDocument();
      expect(await screen.findByText(/clarity/i)).toBeInTheDocument();
      expect(await screen.findByText(/how clear the audio sounds/i)).toBeInTheDocument();
    });

    it("opens modal to create a new metric", async () => {
        (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => ({ metrics: {} }) });
    
        render(<MetricsPage />);
    
        const createButton = await screen.findByRole('button', { name: /\+ create new metric/i });
        fireEvent.click(createButton);
    
        expect(await screen.findByRole('dialog')).toBeInTheDocument();
        expect(screen.getByLabelText(/metric name/i)).toBeInTheDocument();
      });

    it("creates a new metric successfully", async () => {
        (fetch as jest.Mock)
        .mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                metrics: {
                Clarity: {
                    min: 1,
                    max: 5,
                    "minimum label": "Unclear",
                    "maximum label": "Clear",
                    description: "How clear the speech is",
                },
                Naturalness: {
                    min: 1,
                    max: 5,
                    "minimum label": "Robotic",
                    "maximum label": "Natural",
                    description: "How natural the audio sounds",
                },
                Intelligibility: {
                    min: 1,
                    max: 5,
                    "minimum label": "Unintelligible",
                    "maximum label": "Intelligible",
                    description: "How understandable the speech is",
                },
                },
            }),
        }) // initial fetch

        .mockResolvedValueOnce({ ok: true, json: async () => ({}) }) // after POST save

        .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            metrics: {
            // same 3 defaults + the new metric
            Clarity: { /* same */ },
            Naturalness: { /* same */ },
            Intelligibility: { /* same */ },
            Accent: {
                min: 1,
                max: 5,
                "minimum label": "Thick",
                "maximum label": "Neutral",
                description: "How neutral the accent sounds",
            },
            },
        }),
    }); // re-fetch after adding

  render(<MetricsPage />);

  fireEvent.click(await screen.findByRole('button', { name: /\+ create new metric/i }));

  fireEvent.change(screen.getByLabelText(/metric name/i), { target: { value: "Accent" } });
  fireEvent.change(screen.getByLabelText(/minimum value/i), { target: { value: 1 } });
  fireEvent.change(screen.getByLabelText(/maximum value/i), { target: { value: 5 } });
  fireEvent.change(screen.getByLabelText(/minimum label/i), { target: { value: "Thick" } });
  fireEvent.change(screen.getByLabelText(/maximum label/i), { target: { value: "Neutral" } });
  fireEvent.change(screen.getByLabelText(/description/i), { target: { value: "How neutral the accent sounds" } });

  fireEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });
  it("edits an existing metric", async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          metrics: {
            Intelligibility: {
              min: 1,
              max: 5,
              "minimum label": "Unintelligible",
              "maximum label": "Intelligible",
              description: "How understandable the audio is",
            },
          },
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ metrics: {} }) });

    render(<MetricsPage />);

    const editButton = await screen.findByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(screen.getByDisplayValue(/intelligibility/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: "Updated description" } });
    fireEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });

  it("deletes a metric", async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          metrics: {
            Fluency: {
              min: 1,
              max: 5,
              "minimum label": "Disfluent",
              "maximum label": "Fluent",
              description: "How fluent the speaker is",
            },
          },
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ message: "Project metric deleted successfully" }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ metrics: {} }) });

    window.confirm = jest.fn(() => true); // simulate user clicking OK

    render(<MetricsPage />);

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
    });
  });
});
