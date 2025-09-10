import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import { CryptoItem } from "../../../components/CryptoCurrencyList/CryptoItem"; // adjust path as needed

jest.mock("react-router-dom", () => ({
  Link: ({ children, to, ...props }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
}));

jest.mock("@/components/ui/badge", () => ({
  Badge: ({ children, className }) => <span className={className}>{children}</span>,
}));

jest.mock("@/components/WatchlistStarButton", () => ({
  WatchlistStarButton: ({ symbol, isWatched, onToggle }) => (
    <button onClick={() => onToggle(symbol)} data-testid="watchlist-button">
      {isWatched ? "★" : "☆"}
    </button>
  ),
}));

jest.mock("@/lib/utils", () => ({
  cn: (...args) =>
    args
      .map(arg => {
        if (typeof arg === "string") return arg;
        if (typeof arg === "object" && arg !== null) {
          return Object.entries(arg)
            .filter(([_, value]) => Boolean(value))
            .map(([key]) => key)
            .join(" ");
        }
        return "";
      })
      .filter(Boolean)
      .join(" "),
}));

describe("CryptoItem", () => {
  const baseCoin = {
    symbol: "BTC",
    name: "Bitcoin",
    image: "btc.png",
    market_cap_rank: 2,
    price: 12345.6789,
    price_change_24h: 3.45,
  };

  test("renders null if no coin provided", () => {
    const { container } = render(<CryptoItem />);
    expect(container.firstChild).toBeNull();
  });

  test("renders with rank badge and correct styles for top 3 rank", () => {
    render(<CryptoItem coin={baseCoin} />);
    const badge = screen.getByText("#2");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-yellow-50");
  });

  test("renders rank badge with blue styles for rank between 4 and 10", () => {
    render(
      <CryptoItem
        coin={{ ...baseCoin, market_cap_rank: 5 }}
      />
    );
    const badge = screen.getByText("#5");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-blue-50");
  });

  test("renders rank badge with gray styles for rank above 10", () => {
    render(
      <CryptoItem
        coin={{ ...baseCoin, market_cap_rank: 15 }}
      />
    );
    const badge = screen.getByText("#15");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-gray-50");
  });

  test("does not render rank badge if rank is 0 or less", () => {
    render(
      <CryptoItem
        coin={{ ...baseCoin, market_cap_rank: 0 }}
      />
    );
    expect(screen.queryByText(/^#/)).toBeNull();
  });

  test("renders crypto image with alt text and hides on error", () => {
    render(<CryptoItem coin={baseCoin} />);

    const img = screen.getByAltText("Bitcoin logo");
    expect(img).toBeInTheDocument();

    fireEvent.error(img);
    expect(img.style.display).toBe("none");
  });

  test("renders symbol and name correctly", () => {
    render(<CryptoItem coin={baseCoin} />);
    expect(screen.getByText("BTC")).toBeInTheDocument();
    expect(screen.getByText("Bitcoin")).toBeInTheDocument();
  });

  test("PriceDisplay shows formatted price and positive change", () => {
    render(<CryptoItem coin={baseCoin} />);
    expect(screen.getByText("$12,345.6789")).toBeInTheDocument();
    expect(screen.getByText(/↗ 3.45%/)).toBeInTheDocument();
  });

  test("PriceDisplay shows 'N/A' when price is invalid", () => {
    render(
      <CryptoItem
        coin={{ ...baseCoin, price: "not a number", price_change_24h: undefined }}
      />
    );
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  test("PriceDisplay shows negative price change with red badge", () => {
    render(
      <CryptoItem
        coin={{ ...baseCoin, price_change_24h: -5.67 }}
      />
    );
    expect(screen.getByText(/↘ 5.67%/)).toBeInTheDocument();
    const badge = screen.getByText(/↘ 5.67%/);
    expect(badge.className).toMatch(/text-red-500/);
  });

  test("renders WatchlistStarButton with correct props and calls onToggle", () => {
    const onToggleMock = jest.fn();
    render(
      <CryptoItem
        coin={baseCoin}
        isWatched={true}
        onToggleWatchlist={onToggleMock}
      />
    );

    const button = screen.getByTestId("watchlist-button");
    expect(button).toHaveTextContent("★");

    fireEvent.click(button);
    expect(onToggleMock).toHaveBeenCalledWith("BTC");
  });

  test("Link has correct href based on coin symbol", () => {
    render(<CryptoItem coin={baseCoin} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/cryptocurrency/btc");
  });

  test("uses default values if some coin props missing", () => {
    render(
      <CryptoItem
        coin={{
          price: 1000,
          price_change_24h: 0,
        }}
      />
    );
  
    expect(screen.getByText("N/A")).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();
    expect(screen.queryByText(/^#/)).toBeNull();
  });
});
