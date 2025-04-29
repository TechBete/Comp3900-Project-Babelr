import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FileUploadPage from "../pages/app/audioData/[userId]/[projectName]/audioclips"; 
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

jest.mock("components/popout_modal", () => ({
  __esModule: true,
  default: ({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) => (isOpen ? <div>{children}</div> : null),
}));

jest.mock("components/table", () => ({
  __esModule: true,
  default: ({ audioData }: { audioData: any[] }) => (
    <div>
      {audioData.length > 0 ? (
        <div>Audio Table with {audioData.length} files</div>
      ) : (
        <div>No audio files</div>
      )}
    </div>
  ),
}));

jest.mock("components/role_checker", () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe("Researcher File Upload Page", () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      query: { projectName: "TestProject" },
    });
    (global.fetch as jest.Mock) = jest.fn();
  });

  it("renders page correctly and loads audio clips", async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          project: { status: "draft" },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_files: [],
        }),
      });

    render(<FileUploadPage />);

    // heading appears
    expect(await screen.findByRole('heading', { name: /audio library/i })).toBeInTheDocument();

    // shows no audio clips initially
    expect(screen.getByText(/no audio files/i)).toBeInTheDocument();

    // shows sidebar
    expect(screen.getByText(/sidebar for testproject/i)).toBeInTheDocument();

    // shows navbar
    expect(screen.getByText(/mocked navbar/i)).toBeInTheDocument();
  });

  it("opens upload modal and submits a file", async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          project: { status: "draft" },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          audio_files: [],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });


      render(<FileUploadPage />);

      const addButton = await screen.findByRole('button', { name: /\+/i });
      fireEvent.click(addButton);
    
      expect(screen.getByText(/upload new audio/i)).toBeInTheDocument();
    
      const fileInput = screen.getByLabelText(/choose file/i) as HTMLInputElement;
      const dummyFile = new File(["test"], "file_example_WAV_1MG.wav", { type: "audio/wav" });
      fireEvent.change(fileInput, { target: { files: [dummyFile] } });
      
      fireEvent.change(screen.getByLabelText(/model/i), { target: { value: "ModelX" } });
      fireEvent.change(screen.getByLabelText(/language$/i), { target: { value: "English" } }); // <- Fix here
      fireEvent.change(screen.getByLabelText(/language proficiency/i), { target: { value: "native" } });
      fireEvent.change(screen.getByLabelText(/tags/i), { target: { value: "test_tag" } });
      
      fireEvent.click(screen.getByRole('button', { name: /upload/i }));

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(3);
      });
  });
});