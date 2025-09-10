// CryptoCurrencyHeader.test.jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import { CryptoCurrencyHeader } from "../../components/CryptoCurrencyHeader";

jest.mock("react-router-dom", () => ({
  useNavigate: jest.fn(),
}));

jest.mock("@/hooks/useWatchlist", () => ({
  useWatchlist: jest.fn(),
}));

jest.mock("../../components/WatchlistStarButton", () => ({
  WatchlistStarButton: jest.fn(() => <div data-testid="watchlist-btn" />),
}));

describe("CryptoCurrencyHeader", () => {
  let mockNavigate;
  let mockToggle;
  let mockIsWatched;
  let mockWebSocketInstances = [];

  beforeEach(() => {
    jest.clearAllMocks();

    mockNavigate = jest.fn();
    mockToggle = jest.fn();
    mockIsWatched = jest.fn(() => false);

    require("react-router-dom").useNavigate.mockReturnValue(mockNavigate);
    require("@/hooks/useWatchlist").useWatchlist.mockReturnValue({
      loading: false,
      toggleWatchlist: mockToggle,
      isWatched: mockIsWatched,
    });

    // Mock WebSocket
    global.WebSocket = jest.fn((url) => {
      const instance = {
        url,
        readyState: WebSocket.OPEN,
        close: jest.fn(),
        send: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      };
      mockWebSocketInstances.push(instance);
      return instance;
    });
    global.WebSocket.OPEN = 1;
  });

  afterEach(() => {
    mockWebSocketInstances = [];
  });

  test("renders skeletons when image is missing or price is 0", () => {
    render(<CryptoCurrencyHeader symbol="BTC" name="Bitcoin" image="" />);
    const skeletons = screen.getAllByTestId("price-skeleton");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  test("renders price and image when available", () => {
    render(<CryptoCurrencyHeader symbol="ETH" name="Ethereum" image="eth.png" />);
    act(() => {
      // Simulate WebSocket message
      const wsInstance = mockWebSocketInstances[0];
      const message = JSON.stringify({ k: { c: "3000.55" } });
      wsInstance.onmessage({ data: message });
    });
    expect(screen.getByText("ETH")).toBeInTheDocument();
    expect(screen.getByText("$3000.55")).toBeInTheDocument();
    expect(screen.getByAltText("Ethereum logo")).toBeInTheDocument();
  });

  test("navigates home when back button clicked", () => {
    render(<CryptoCurrencyHeader symbol="BTC" name="Bitcoin" image="" />);
    fireEvent.click(screen.getByRole("button"));
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });

  test("passes correct props to WatchlistStarButton", () => {
    mockIsWatched.mockReturnValue(true);
    render(<CryptoCurrencyHeader symbol="DOGE" name="Dogecoin" image="" />);
    const WatchlistStarButton = require("../../components/WatchlistStarButton").WatchlistStarButton;
    expect(WatchlistStarButton.mock.calls[0][0]).toEqual(
      expect.objectContaining({
        loading: false,
        symbol: "DOGE",
        onToggle: mockToggle,
        isWatched: true,
        size: "lg",
      })
    );
  });

  test("closes WebSocket on unmount", () => {
    const { unmount } = render(<CryptoCurrencyHeader symbol="ADA" name="Cardano" image="" />);
    const wsInstance = mockWebSocketInstances[0];
    unmount();
    expect(wsInstance.close).toHaveBeenCalled();
  });
});
