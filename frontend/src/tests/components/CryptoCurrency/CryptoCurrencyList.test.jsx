import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { MemoryRouter } from "react-router-dom";

jest.mock("../../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

jest.mock("../../../hooks/useCryptoData", () => ({
  useCryptoData: jest.fn(),
}));
jest.mock("../../../hooks/useWatchlist", () => ({
  useWatchlist: jest.fn(),
}));

jest.mock("@/components/CryptoCurrencyList/CryptoItem", () => ({
  CryptoItem: ({ coin }) => <div>{coin.name}</div>,
}));

import { CryptoCurrencyList } from "../../../components/CryptoCurrencyList/CryptoCurrencyList";
import { useCryptoData } from "../../../hooks/useCryptoData";
import { useWatchlist } from "../../../hooks/useWatchlist";

describe("CryptoCurrencyList", () => {
  const baseCryptoData = {
    allCrypto: [
      { symbol: "BTC", name: "Bitcoin" },
      { symbol: "ETH", name: "Ethereum" },
    ],
    tierLimit: 1,
    tierLabel: "BASIC",
    loading: false,
    error: null,
    refetch: jest.fn(),
    lastUpdated: "2 mins ago",
  };

  const baseWatchlistData = {
    loading: false,
    toggleWatchlist: jest.fn(),
    isWatched: jest.fn().mockReturnValue(false),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders loading skeleton when loading", () => {
    useCryptoData.mockReturnValue({ ...baseCryptoData, loading: true });
    useWatchlist.mockReturnValue(baseWatchlistData);

    render(<CryptoCurrencyList />);
    expect(screen.getByText(/All Cryptocurrencies/i)).toBeInTheDocument();
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0);
  });

  test("renders error state and allows retry", () => {
    const mockRefetch = jest.fn();
    useCryptoData.mockReturnValue({
      ...baseCryptoData,
      error: "Failed to load data",
      refetch: mockRefetch,
    });
    useWatchlist.mockReturnValue(baseWatchlistData);

    render(<CryptoCurrencyList />);
    expect(screen.getByText(/Error Loading Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Failed to load data/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Try Again/i }));
    expect(mockRefetch).toHaveBeenCalled();
  });

  test("renders list of cryptocurrencies within tier limit", () => {
    useCryptoData.mockReturnValue(baseCryptoData);
    useWatchlist.mockReturnValue(baseWatchlistData);

    render(
      <MemoryRouter>
        <CryptoCurrencyList />
      </MemoryRouter>
    );

    expect(screen.getByText(/Bitcoin/)).toBeInTheDocument();
    expect(screen.queryByText(/Ethereum/)).not.toBeInTheDocument(); // beyond tier limit
    expect(screen.getByText(/BASIC/)).toBeInTheDocument();
  });

  test("renders empty state when no crypto data", () => {
    useCryptoData.mockReturnValue({ ...baseCryptoData, allCrypto: [] });
    useWatchlist.mockReturnValue(baseWatchlistData);
    
    render(
      <MemoryRouter>
        <CryptoCurrencyList />
      </MemoryRouter>
    );
    
    expect(
      screen.getByText(/No cryptocurrency data available/i)
    ).toBeInTheDocument();
  });

  test("shows upgrade prompt when tier is not PREMIUM and more coins exist", () => {
    useCryptoData.mockReturnValue({
      ...baseCryptoData,
      allCrypto: [
        { symbol: "BTC", name: "Bitcoin" },
        { symbol: "ETH", name: "Ethereum" },
      ],
      tierLimit: 1,
      tierLabel: "BASIC",
    });
    useWatchlist.mockReturnValue(baseWatchlistData);

    render(
      <MemoryRouter>
        <CryptoCurrencyList />
      </MemoryRouter>
    );

    expect(
      screen.getByText(/Upgrade your plan/i)
    ).toBeInTheDocument();
  });

  test("shows last updated info when available", () => {
    useCryptoData.mockReturnValue(baseCryptoData);
    useWatchlist.mockReturnValue(baseWatchlistData);

    render(
      <MemoryRouter>
        <CryptoCurrencyList />
      </MemoryRouter>
    );

    expect(screen.getByText(/Updated 2 mins ago/i)).toBeInTheDocument();
  });
});
