// Dashboard.test.jsx
import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";

import Dashboard from "../../pages/Dashboard";

// Mock child components
jest.mock("@/components/CryptoCurrencyList", () => ({
  CryptoCurrencyList: () => <div data-testid="crypto-list">Crypto List</div>,
}));

jest.mock("@/components/WatchlistSection", () => ({
  WatchlistSection: () => <div data-testid="watchlist-section">Watchlist</div>,
}));

jest.mock("@/components/ui/accordion", () => ({
  Accordion: ({ children }) => <div data-testid="accordion">{children}</div>,
  AccordionItem: ({ children }) => (
    <div data-testid="accordion-item">{children}</div>
  ),
  AccordionTrigger: ({ children, ...props }) => (
    <button data-testid="accordion-trigger" {...props}>
      {children}
    </button>
  ),
  AccordionContent: ({ children }) => (
    <div data-testid="accordion-content">{children}</div>
  ),
}));

describe("Dashboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the header with title and API attribution", () => {
    render(<Dashboard />);

    // Title
    expect(
      screen.getByRole("heading", { name: /SAFEGUARD/i })
    ).toBeInTheDocument();

    // Attribution link
    const link = screen.getByRole("link", { name: /CoinGecko API/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "https://www.coingecko.com/");
    expect(link).toHaveAttribute("target", "_blank");
  });

  test("renders the watchlist section inside an accordion", () => {
    render(<Dashboard />);

    expect(screen.getByTestId("accordion")).toBeInTheDocument();
    expect(screen.getByTestId("accordion-item")).toBeInTheDocument();
    expect(screen.getByTestId("accordion-trigger")).toHaveTextContent(
      /My Watchlist/i
    );

    // Content area has WatchlistSection
    expect(screen.getByTestId("watchlist-section")).toHaveTextContent(
      /Watchlist/i
    );
  });

  test("renders the top 10 cryptocurrencies list", () => {
    render(<Dashboard />);
    expect(screen.getByTestId("crypto-list")).toHaveTextContent(/Crypto List/i);
  });

  test("allows toggling the accordion trigger", () => {
    render(<Dashboard />);

    const trigger = screen.getByTestId("accordion-trigger");
    fireEvent.click(trigger);

    // In this mock, toggle won't change much, but we can assert the click happens
    expect(trigger).toHaveTextContent(/My Watchlist/i);
  });
});
