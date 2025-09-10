// Cryptocurrency.test.jsx
import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import '@testing-library/jest-dom';
import axios from "axios";
import { useParams } from "react-router-dom";

import Cryptocurrency from "../../pages/Cryptocurrency";

// Mock axios
jest.mock("axios");

jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

// Mock useParams
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useParams: jest.fn(),
}));

beforeEach(() => {
  useParams.mockReturnValue({ id: "eth" });
});

// Mock child components (we don’t need to test their internal logic here)
jest.mock("@/components/CryptoCurrencyGraph", () => ({
  CryptoCurrencyGraph: () => <div data-testid="crypto-graph" />,
}));
jest.mock("@/components/CryptoCurrencyHeader", () => ({
  CryptoCurrencyHeader: ({ symbol, name }) => (
    <div data-testid="crypto-header">{symbol} - {name}</div>
  ),
}));
jest.mock("@/components/NewsHub", () => () => <div data-testid="news-hub" />);
jest.mock("@/components/PurchasePlatformsList", () => ({
  PurchasePlatformsList: ({ platforms }) => (
    <div data-testid="purchase-platforms">{platforms.length} platforms</div>
  ),
}));
jest.mock("@/components/SentimentCard", () => () => <div data-testid="sentiment-card" />);
jest.mock("@/components/StatsCard", () => () => <div data-testid="stats-card" />);

describe("ExpandableDescription", () => {
  const ExpandableDescription = ({ description, name }) => {
    // Import from file instead of re-defining in real test
    const { ExpandableDescription } = jest.requireActual("../../pages/Cryptocurrency");
    return <ExpandableDescription description={description} name={name} />;
  };

  test("renders full description if less than 200 chars", () => {
    render(<ExpandableDescription description="Short description" name="Bitcoin" />);
    expect(screen.getByText(/What is Bitcoin/i)).toBeInTheDocument();
    expect(screen.getByText(/Short description/i)).toBeInTheDocument();
    expect(screen.queryByText(/Read More/i)).not.toBeInTheDocument();
  });

  test("toggles description in full component", async () => {
    axios.get
      .mockResolvedValueOnce({
        data: {
          name: "Ethereum",
          description: "a".repeat(250),
          image: "eth.png",
          categories: [],
          homepage_url: "https://ethereum.org",
          purchase_platforms: [],
          volume: 0,
          marketcap: 0,
        },
      })
      .mockResolvedValueOnce({ data: { normalised_up_percentage: 0.8, normalised_down_percentage: 0.2 } })
      .mockResolvedValueOnce({ data: { rsi: 50, macd: 0.5, ema: 200 } });
  
    render(<Cryptocurrency />);
  
    await waitFor(() => {
      expect(screen.getByText(/Read More/i)).toBeInTheDocument();
    });
  
    fireEvent.click(screen.getByText(/Read More/i));
    expect(screen.getByText(/Read Less/i)).toBeInTheDocument();
  });
});

describe("Cryptocurrency", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useParams.mockReturnValue({ id: "eth" });
  });

  test("fetches metadata, sentiment, and indicators on mount", async () => {
    axios.get
      .mockResolvedValueOnce({
        data: {
          name: "Ethereum",
          description: "Ethereum description",
          image: "eth.png",
          categories: [],
          homepage_url: "https://ethereum.org",
          purchase_platforms: [{ name: "Binance" }],
          volume: 123,
          marketcap: 456,
        },
      })
      .mockResolvedValueOnce({
        data: {
          normalised_up_percentage: 0.8,
          normalised_down_percentage: 0.2,
        },
      })
      .mockResolvedValueOnce({
        data: { rsi: 50, macd: 0.5, ema: 200 },
      });

    render(<Cryptocurrency />);

    // Wait for header
    await waitFor(() => {
      expect(screen.getByTestId("crypto-header")).toHaveTextContent("ETH - Ethereum");
    });

    expect(screen.getByTestId("crypto-graph")).toBeInTheDocument();
    expect(screen.getByTestId("sentiment-card")).toBeInTheDocument();
    expect(screen.getByTestId("stats-card")).toBeInTheDocument();
    expect(screen.getByTestId("news-hub")).toBeInTheDocument();
    expect(screen.getByText(/Official Website/i)).toHaveAttribute("href", "https://ethereum.org");
    expect(screen.getByTestId("purchase-platforms")).toHaveTextContent("1 platforms");

    // API calls
    expect(axios.get).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining("/api/crypto/metadata"),
      expect.objectContaining({ params: { symbol: "ETH" } })
    );
    expect(axios.get).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining("/api/crypto/sentiment/all"),
      expect.objectContaining({ params: { symbol: "ETH" } })
    );
    expect(axios.get).toHaveBeenNthCalledWith(
      3,
      expect.stringContaining("/api/crypto/latest_indicators"),
      expect.objectContaining({ params: { symbol: "ETH" } })
    );
  });

  test("handles API errors gracefully", async () => {
    axios.get
      .mockRejectedValueOnce(new Error("metadata error"))
      .mockRejectedValueOnce(new Error("sentiment error"))
      .mockRejectedValueOnce(new Error("indicator error"));

    render(<Cryptocurrency />);

    await waitFor(() => {
      expect(screen.getByTestId("crypto-header")).toHaveTextContent("ETH -");
    });

    expect(screen.getByTestId("crypto-graph")).toBeInTheDocument();
    expect(screen.getByTestId("news-hub")).toBeInTheDocument();
  });
});
