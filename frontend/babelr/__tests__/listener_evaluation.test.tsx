import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Evaluation from "../pages/Listener/evaluation";
import '@testing-library/jest-dom';

jest.mock("components/nav_bar_listener", () => {
  return {
    __esModule: true,
    default: () => <nav>Mocked Navbar</nav>,
  };
});

jest.mock("components/role_checker", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

describe("Listener Evaluation Page", () => {
  beforeAll(() => {
    global.URL.createObjectURL = jest.fn(() => "mock-audio-url");
  });
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("renders evaluation page properly", async () => {
    // Mock fetch responses
    (global.fetch as jest.Mock) = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_file: "test-audio-id",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_file: {
            metrics: {
              Clarity: { min: 1, max: 5, "minimum label": "Unclear", "maximum label": "Clear", description: "Clarity description" },
              Intelligibility: { min: 1, max: 5, "minimum label": "Unintelligible", "maximum label": "Intelligible", description: "Intelligibility description" },
              Naturalness: { min: 1, max: 5, "minimum label": "Robotic", "maximum label": "Natural", description: "Naturalness description" },
            },
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(["dummy audio content"], { type: "audio/mpeg" }),
      });

    render(<Evaluation />);

    // Confirm page loads
    expect(await screen.findByRole('heading', { name: /audio evaluation/i })).toBeInTheDocument();
    expect(screen.getByText(/play the audio clip and rate it based on the provided metrics/i)).toBeInTheDocument();
    const audioElement = document.getElementById('audio');
    expect(audioElement).toBeInTheDocument();
  });

  it("submits ratings successfully", async () => {
    // Mock fetch for initial loading
    (global.fetch as jest.Mock) = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_file: "test-audio-id",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_file: {
            metrics: {
              Clarity: { min: 1, max: 5, "minimum label": "Unclear", "maximum label": "Clear", description: "Clarity description" },
              Intelligibility: { min: 1, max: 5, "minimum label": "Unintelligible", "maximum label": "Intelligible", description: "Intelligibility description" },
              Naturalness: { min: 1, max: 5, "minimum label": "Robotic", "maximum label": "Natural", description: "Naturalness description" },
            },
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(["dummy audio content"], { type: "audio/mpeg" }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

    render(<Evaluation />);

    // Wait until page shows up
    await screen.findByRole('heading', { name: /audio evaluation/i });


    // Submit the rating
    fireEvent.click(screen.getByRole('button', { name: /submit rating/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8016/listener/submitRating",
        expect.objectContaining({
          method: "POST",
        })
      );
    });
  });
});