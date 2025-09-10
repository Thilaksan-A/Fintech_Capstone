// News.test.jsx
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import '@testing-library/jest-dom';
import axios from "axios";

import News from "../../pages/News";

// Mock BigNewsCard
jest.mock("@/components/BigNewsCard", () => ({
  BigNewsCard: ({ data }) => (
    <div data-testid="big-news-card">
      {data && data.title ? data.title : "Placeholder"}
    </div>
  ),
}));

jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

// Mock axios
jest.mock("axios");

describe("News", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading placeholders when no data is returned", async () => {
    axios.get.mockResolvedValueOnce({ data: [] });

    render(<News />);

    // Wait for axios call to complete
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("/api/crypto/news"),
        expect.objectContaining({
          params: { query: "cryptocurrency", refresh: false },
        })
      );
    });

    // Should render 2 placeholder cards
    const cards = screen.getAllByTestId("big-news-card");
    expect(cards).toHaveLength(2);
    expect(cards[0]).toHaveTextContent("Placeholder");
  });

  it("renders news articles when API returns data", async () => {
    const mockArticles = Array.from({ length: 3 }, (_, i) => ({
      title: `Article ${i + 1}`,
    }));
    axios.get.mockResolvedValueOnce({ data: mockArticles });

    render(<News />);

    await waitFor(() => {
      expect(screen.getByText("Article 1")).toBeInTheDocument();
    });

    const cards = screen.getAllByTestId("big-news-card");
    expect(cards).toHaveLength(3);
    expect(cards[0]).toHaveTextContent("Article 1");
    expect(cards[1]).toHaveTextContent("Article 2");
    expect(cards[2]).toHaveTextContent("Article 3");
  });

  it("limits articles to 15 items", async () => {
    const mockArticles = Array.from({ length: 20 }, (_, i) => ({
      title: `Article ${i + 1}`,
    }));
    axios.get.mockResolvedValueOnce({ data: mockArticles });

    render(<News />);

    await waitFor(() => {
      const cards = screen.getAllByTestId("big-news-card");
      expect(cards).toHaveLength(15);
    });
  });

  it("handles API errors gracefully", async () => {
    jest.spyOn(console, "error").mockImplementation(() => {}); // Suppress error log
    axios.get.mockRejectedValueOnce(new Error("Network error"));

    render(<News />);

    await waitFor(() => {
      expect(screen.getAllByTestId("big-news-card")).toHaveLength(2);
    });

    console.error.mockRestore();
  });
});
