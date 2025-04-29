import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import AnalyticsPage from "pages/app/audioData/[userId]/[projectName]/analytics";
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

jest.mock("components/analytics/rating_chart", () => ({
  __esModule: true,
  default: ({ data }: any) => <div>Mocked RatingChart with {data.length} items</div>,
}));

jest.mock("components/analytics/demographics_box", () => ({
  __esModule: true,
  default: ({ projectName }: { projectName: string }) => <div>Demographics for {projectName}</div>,
}));

jest.mock("components/analytics/rating_table", () => ({
  __esModule: true,
  default: ({ data }: any) => <div>RatingsTable with {data.length} entries</div>,
}));

jest.mock("components/analytics/metric_picker", () => ({
  __esModule: true,
  default: ({ onMetricSelect }: { onMetricSelect: (metric: string) => void }) => (
    <button onClick={() => onMetricSelect('Naturalness')}>Select Naturalness</button>
  ),
}));

jest.mock("components/analytics/rating_summary_table", () => ({
  __esModule: true,
  default: ({ data }: any) => <div>RatingsSummaryTable with {data.length} rows</div>,
}));

jest.mock("components/analytics/export_button", () => ({
  __esModule: true,
  default: () => <div>Export Buttons</div>,
}));

jest.mock("components/role_checker", () => ({
  __esModule: true,
  default: ({ children }: any) => <>{children}</>,
}));

describe("Researcher Analytics Page", () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      query: { projectName: "TestProject" },
    });

    (global.fetch as jest.Mock) = jest.fn();
  });

  it("renders analytics dashboard with summary, graph, demographics and table", async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          rating_stats: [
            { audio: "clip1", model: "ModelA", language: "English", ratings: [3, 4, 5] },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          summary_stats: [
            { clipId: "clip1", metric: "Naturalness", model: "ModelA", mean: 4.5, std: 0.5, ci_low: 4.0, ci_high: 5.0 },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          graph_stats: [
            { metric: "Naturalness", model: "ModelA", mean: 4.5, std: 0.5, ci_low: 4.0, ci_high: 5.0 },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          rating_stats: [
            { audio: "clip1", model: "ModelA", language: "English", ratings: [3, 4, 5] },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          summary_stats: [
            { clipId: "clip1", metric: "Naturalness", model: "ModelA", mean: 4.5, std: 0.5, ci_low: 4.0, ci_high: 5.0 },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          graph_stats: [
            { metric: "Naturalness", model: "ModelA", mean: 4.5, std: 0.5, ci_low: 4.0, ci_high: 5.0 },
          ],
        }),
      });
    

    render(<AnalyticsPage />);

    // Navbar and Sidebar
    expect(await screen.findByText(/mocked navbar/i)).toBeInTheDocument();
    expect(screen.getByText(/sidebar for testproject/i)).toBeInTheDocument();

    // Summary Statistics Table
    expect(await screen.findByText(/ratingssummarytable with 1 rows/i)).toBeInTheDocument();

    // Graph Statistics Chart
    expect(await screen.findByText(/mocked ratingchart with 1 items/i)).toBeInTheDocument();

    // Demographics
    expect(screen.getByText(/demographics for testproject/i)).toBeInTheDocument();

    // Raw Ratings Table
    expect(await screen.findByText(/ratingstable with 1 entries/i)).toBeInTheDocument();

    // Export buttons present
    expect(screen.getByText(/export buttons/i)).toBeInTheDocument();

    // Simulate Metric Picker Interaction
    fireEvent.click(screen.getByRole('button', { name: /select naturalness/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6); // 3 initial + 3 new after metric change
    });
  });
});