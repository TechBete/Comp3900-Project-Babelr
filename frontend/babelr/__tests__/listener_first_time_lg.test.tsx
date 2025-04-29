import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import LanguageSelector from "../pages/Listener/first_time_listener_lg"; 
import { useRouter } from "next/router";
import '@testing-library/jest-dom';

// mocks
jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));
jest.mock("components/role_checker", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

describe("Language Selector Page", () => {
  const pushMock = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
    });
    pushMock.mockReset();
  });

  it("renders the language selector page", () => {
    render(<LanguageSelector />);
    expect(screen.getByRole('heading', { name: /select your languages/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add language/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
  });

  it("adds a language entry", () => {
    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));

    expect(screen.getAllByRole('combobox')).toHaveLength(2); // 1 for language, 1 for proficiency
  });

  it("fills a language and proficiency", () => {
    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));

    fireEvent.change(screen.getAllByRole('combobox')[0], { target: { value: 'English' } });
    fireEvent.change(screen.getAllByRole('combobox')[1], { target: { value: 'native' } });

    expect(screen.getAllByRole('combobox')[0]).toHaveValue('English');
    expect(screen.getAllByRole('combobox')[1]).toHaveValue('native');
  });

  it("removes a language entry", () => {
    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));

    const removeButton = screen.getByRole('button', { name: /✕/i });
    fireEvent.click(removeButton);

    expect(screen.queryAllByRole('combobox')).toHaveLength(0);
  });

  it("submits form successfully and redirects", async () => {
    (global.fetch as jest.Mock) = jest.fn()
      .mockResolvedValue({ ok: true, json: async () => ({}) });

    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));
    fireEvent.change(screen.getAllByRole('combobox')[0], { target: { value: 'English' } });
    fireEvent.change(screen.getAllByRole('combobox')[1], { target: { value: 'native' } });

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/Listener/home_listener");
    });
  });

  it("shows server error on failed submission", async () => {
    (global.fetch as jest.Mock) = jest.fn()
      .mockResolvedValue({ ok: false, json: async () => ({ error: "Failed to add language" }) });

    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));
    fireEvent.change(screen.getAllByRole('combobox')[0], { target: { value: 'English' } });
    fireEvent.change(screen.getAllByRole('combobox')[1], { target: { value: 'native' } });

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to add language/i)).toBeInTheDocument();
    });
  });

  it("shows network error on fetch rejection", async () => {
    (global.fetch as jest.Mock) = jest.fn()
      .mockRejectedValue(new Error('Network Error'));

    render(<LanguageSelector />);
    fireEvent.click(screen.getByRole('button', { name: /add language/i }));
    fireEvent.change(screen.getAllByRole('combobox')[0], { target: { value: 'English' } });
    fireEvent.change(screen.getAllByRole('combobox')[1], { target: { value: 'native' } });

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText(/network error: fetch request failed/i)).toBeInTheDocument();
    });
  });

});