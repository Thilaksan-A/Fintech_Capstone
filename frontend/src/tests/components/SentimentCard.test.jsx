import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import "@testing-library/jest-dom";
import axios from "axios";
import { useQuery } from "@tanstack/react-query";

import SentimentCard, { fetchForecast } from "../../components/SentimentCard";

jest.mock("@tanstack/react-query", () => ({
  useQuery: jest.fn(),
}));

jest.mock('../../config', () => ({
  API_BASE_URL: "https://mock-api.com",
}));

jest.mock("axios");

describe("fetchForecast", () => {
  const { fetchForecast } = jest.requireActual("../../components/SentimentCard");

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("throws an error if no token is present", async () => {
    await expect(fetchForecast("BTC")).rejects.toThrow("Authentication required");
  });

  test("calls axios with correct params when token exists", async () => {
    localStorage.setItem("token", "fake-token");
    axios.post.mockResolvedValueOnce({ data: { ok: true } });

    const data = await fetchForecast("BTC");

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining("/api/crypto/forecast"),
      { symbol: "BTC" },
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer fake-token",
        }),
      })
    );
    expect(data).toEqual({ ok: true });
  });
});

describe("SentimentCard component", () => {
  const mockCrypto = { symbol: "BTC" };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem("token", "test-token");
  });

  test("renders loading state", () => {
    useQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: jest.fn(),
      isRefetching: false,
    });
  
    render(<SentimentCard crypto={mockCrypto} />);
  
    const skeletons = screen.getAllByRole("generic", { hidden: true })
      .filter(el => el.getAttribute("data-slot") === "skeleton");
  
    expect(skeletons.length).toBeGreaterThan(0);
  });

  test("renders error state and retries on click", () => {
    const refetch = jest.fn();
    useQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: { message: "Network Error" },
      refetch,
      isRefetching: false,
    });

    render(<SentimentCard crypto={mockCrypto} />);
    expect(screen.getByText("Network Error")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(refetch).toHaveBeenCalled();
  });

  test("renders empty state when no sentiment data", () => {
    const refetch = jest.fn();
    useQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
      refetch,
      isRefetching: false,
    });

    render(<SentimentCard crypto={mockCrypto} />);
    expect(screen.getByText(/No sentiment data available/i)).toBeInTheDocument();
  });

  test("renders populated state with reasoning", () => {
    useQuery.mockReturnValue({
      data: {
        recommendation: "BUY",
        up_5pct_24h: 42.5,
        reasoning: "Strong upward trend detected",
      },
      isLoading: false,
      error: null,
      refetch: jest.fn(),
      isRefetching: false,
    });
  
    render(<SentimentCard crypto={mockCrypto} />);
  
    // test's in the DOM but hidden until we expand
    fireEvent.click(screen.getByRole("button", { name: /View Forecast Analysis/i }));
  
    expect(
      screen.getByText(/Strong upward trend detected/i)
    ).toBeInTheDocument();
  });

  test("refresh button triggers refetch", () => {
    const refetch = jest.fn();
    useQuery.mockReturnValue({
      data: {
        recommendation: "HOLD",
        up_5pct_24h: null,
        reasoning: "",
      },
      isLoading: false,
      error: null,
      refetch,
      isRefetching: false,
    });

    render(<SentimentCard crypto={mockCrypto} />);
    fireEvent.click(screen.getByRole("button", { name: "" })); // ghost refresh button has no accessible name
    expect(refetch).toHaveBeenCalled();
  });
});
