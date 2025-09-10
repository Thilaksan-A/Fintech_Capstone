// CryptoCurrencyGraph.test.jsx
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import { CryptoCurrencyGraph } from "../../components/CryptoCurrencyGraph";

jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

jest.mock("../../components/PriceGraph", () => ({
  PriceGraph: jest.fn(() => <div data-testid="price-graph" />),
}));
jest.mock("../../components/ExpertGraph", () => ({
  ExpertGraph: jest.fn(() => <div data-testid="expert-graph" />),
}));

const mockNow = new Date("2025-08-11T12:00:00Z");

describe("CryptoCurrencyGraph", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });
  
  beforeEach(() => {
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => [],
    });
  });
  
  afterEach(() => {
    jest.restoreAllMocks();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  function mockFetchOk(data) {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => data,
    });
  }

  function mockFetchError(status = 500, message = "Server error") {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status,
      json: async () => ({ message }),
    });
  }

  test("shows loading state initially", async () => {
    mockFetchOk([]);
    render(<CryptoCurrencyGraph symbol="BTC" />);
    expect(screen.getByText(/1D/i)).toBeInTheDocument(); // timeframe button
    expect(screen.getByTestId("price-skeleton")).toBeTruthy; // GraphSkeleton skeleton
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  });

  test("renders success state with PriceGraph", async () => {
    const mockData = [
      { timestamp: "2025-08-11T11:30:00Z", value: 50000 },
      { timestamp: "2025-08-11T10:30:00Z", value: 49000 },
    ];
    mockFetchOk(mockData);

    render(<CryptoCurrencyGraph symbol="ETH" />);

    await waitFor(() => {
      expect(screen.getByTestId("price-graph")).toBeInTheDocument();
    });

    const PriceGraph = require("../../components/PriceGraph").PriceGraph;
    expect(PriceGraph).toHaveBeenCalledWith(
      expect.objectContaining({
        symbol: "ETH",
        data: mockData,
        formatLabel: expect.any(Function),
      }),
      undefined
    );
  });

  test("renders error state and retries on button click", async () => {
    mockFetchError();
    render(<CryptoCurrencyGraph symbol="DOGE" />);

    await waitFor(() =>
      expect(screen.getByText(/Failed to load chart data/i)).toBeInTheDocument()
    );

    mockFetchOk([]);
    fireEvent.click(screen.getByRole("button", { name: /Retry/i }));
    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(2));
  });

  test("renders empty state when no data", async () => {
    mockFetchOk([]);
    render(<CryptoCurrencyGraph symbol="ADA" />);
    await waitFor(() =>
      expect(screen.getByText(/No chart data available/i)).toBeInTheDocument()
    );
  });

  test("changes timeframe and fetches new data", async () => {
    render(<CryptoCurrencyGraph symbol="SOL" />);
  
    // Wait for initial fetch call on mount
    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(1));
    
    await screen.findByText("3M");
    fireEvent.click(screen.getByText("3M"));
    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(2));
    
    // Verify the last fetch URL contains interval=7D
    expect(global.fetch).toHaveBeenLastCalledWith(
      expect.stringContaining("interval=3M")
    );
  });

  test("shows DataRangeAlert when latest data is older than 1 hour", async () => {
    const mockData = [
      { timestamp: "2025-08-11T09:00:00Z", value: 50000 },
      { timestamp: "2025-08-10T09:00:00Z", value: 49000 },
    ];
    mockFetchOk(mockData);
    render(<CryptoCurrencyGraph symbol="XRP" />);
    await waitFor(() =>
      expect(
        screen.getByText(/Data not current/i)
      ).toBeInTheDocument()
    );
  });
});
