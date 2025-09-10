import { render, screen } from "@testing-library/react";
import React from "react";

import { WatchlistSection } from "../../components/WatchlistSection";

// Mock hooks
jest.mock("@/hooks/useWatchlist", () => ({
  useWatchlist: jest.fn(),
}));
jest.mock("@/hooks/useCryptoData", () => ({
  useCryptoData: jest.fn(),
}));

// Mock child component to make assertions easier
jest.mock("@/components/CryptoCurrencyList/CryptoItem", () => ({
  CryptoItem: ({ coin }) => <div data-testid="crypto-item">{coin.symbol}</div>,
}));

import { useCryptoData } from "@/hooks/useCryptoData";
import { useWatchlist } from "@/hooks/useWatchlist";

describe("WatchlistSection", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading skeleton when loading", () => {
    useWatchlist.mockReturnValue({
      watchlist: new Set(),
      loading: true,
      error: null,
      toggleWatchlist: jest.fn(),
      isWatched: jest.fn(),
    });
    useCryptoData.mockReturnValue({
      allCrypto: [],
      loading: false,
    });

    render(<WatchlistSection />);
    expect(screen.getAllByTestId("skeleton").length).toBeGreaterThan(0);
  });

  test("renders error state", () => {
    useWatchlist.mockReturnValue({
      watchlist: new Set(),
      loading: false,
      error: "Something went wrong",
      toggleWatchlist: jest.fn(),
      isWatched: jest.fn(),
    });
    useCryptoData.mockReturnValue({
      allCrypto: [],
      loading: false,
    });

    render(<WatchlistSection />);
    expect(
      screen.getByText(/Failed to load watchlist: Something went wrong/i)
    ).toBeInTheDocument();
  });

  test("renders empty watchlist state", () => {
    useWatchlist.mockReturnValue({
      watchlist: new Set(),
      loading: false,
      error: null,
      toggleWatchlist: jest.fn(),
      isWatched: jest.fn(),
    });
    useCryptoData.mockReturnValue({
      allCrypto: [],
      loading: false,
    });

    render(<WatchlistSection />);
    expect(
      screen.getByText(/Your watchlist is empty/i)
    ).toBeInTheDocument();
  });

  test("renders watchlist items when data matches", () => {
    useWatchlist.mockReturnValue({
      watchlist: new Set(["BTC", "ETH"]),
      loading: false,
      error: null,
      toggleWatchlist: jest.fn(),
      isWatched: jest.fn(() => true),
    });
    useCryptoData.mockReturnValue({
      allCrypto: [
        { symbol: "BTC", market_cap_rank: 1 },
        { symbol: "ETH", market_cap_rank: 2 },
        { symbol: "DOGE", market_cap_rank: 3 },
      ],
      loading: false,
    });

    render(<WatchlistSection />);
    expect(screen.getAllByTestId("crypto-item")).toHaveLength(2);
    expect(screen.getByText("BTC")).toBeInTheDocument();
    expect(screen.getByText("ETH")).toBeInTheDocument();
  });

  test("renders fallback when watchlist has no matching crypto data", () => {
    useWatchlist.mockReturnValue({
      watchlist: new Set(["XRP"]),
      loading: false,
      error: null,
      toggleWatchlist: jest.fn(),
      isWatched: jest.fn(),
    });
    useCryptoData.mockReturnValue({
      allCrypto: [],
      loading: false,
    });

    render(<WatchlistSection />);
    expect(
      screen.getByText(
        /Your watched cryptocurrencies will appear here when price data is available/i
      )
    ).toBeInTheDocument();
  });
});
