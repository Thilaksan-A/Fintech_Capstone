import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import StatsCard from "../../components/StatsCard";

describe("StatsCard", () => {
  const sampleCrypto = {
    stats: {
      marketCap: 5000000000,
      volume: 75000000,
      macd: 0.1234,
      ema: 123.45,
      rsi: 72,
      sentiment: 65,
    },
  };

  test("renders 'No statistics available' when crypto.stats is missing", () => {
    render(<StatsCard crypto={{}} />);
    expect(screen.getByText(/No statistics available/i)).toBeInTheDocument();
    expect(screen.getByText(/Statistics data is not available/i)).toBeInTheDocument();
  });

  test("renders primary stats with correct formatting", () => {
    render(<StatsCard crypto={sampleCrypto} />);

    expect(screen.getByText("Market Cap")).toBeInTheDocument();
    expect(screen.getByText("$5.00B")).toBeInTheDocument();

    expect(screen.getByText("24h Volume")).toBeInTheDocument();
    expect(screen.getByText("$75.00M")).toBeInTheDocument();
  });

  test("renders initial technical stats (2 only)", () => {
    render(<StatsCard crypto={sampleCrypto} />);

    expect(screen.getByText("MACD")).toBeInTheDocument();
    expect(screen.getByText("0.1234")).toBeInTheDocument();
    expect(screen.getByText("EMA")).toBeInTheDocument();
    expect(screen.getByText("$123.45")).toBeInTheDocument();

    expect(screen.queryByText("RSI")).not.toBeInTheDocument();
    expect(screen.queryByText("Sentiment")).not.toBeInTheDocument();
  });

  test("shows all technical stats when 'Show More' is clicked", () => {
    render(<StatsCard crypto={sampleCrypto} />);
    fireEvent.click(screen.getByRole("button", { name: /Show More/i }));

    expect(screen.getByText("RSI")).toBeInTheDocument();
    expect(screen.getByText("72.0")).toBeInTheDocument();

    expect(screen.getByText("Sentiment")).toBeInTheDocument();
    expect(screen.getByText("65.00")).toBeInTheDocument();
  });

  test("toggles back to 2 stats when 'Show Less' is clicked", () => {
    render(<StatsCard crypto={sampleCrypto} />);
    const toggleButton = screen.getByRole("button", { name: /Show More/i });

    fireEvent.click(toggleButton);
    expect(screen.getByText("RSI")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Show Less/i }));
    expect(screen.queryByText("RSI")).not.toBeInTheDocument();
  });

  test("renders indicator badges for MACD, RSI, and Sentiment", () => {
    render(<StatsCard crypto={sampleCrypto} />);
    fireEvent.click(screen.getByRole("button", { name: /Show More/i }));

    expect(screen.getByTestId("macd-indicator")).toHaveTextContent("Bullish");
    expect(screen.getByText("Overbought")).toBeInTheDocument();
  });

  test("renders progress bars for RSI and Sentiment", () => {
    render(<StatsCard crypto={sampleCrypto} />);
    fireEvent.click(screen.getByRole("button", { name: /Show More/i }));

    const progressBars = screen.getAllByRole("progressbar");
    expect(progressBars.length).toBeGreaterThanOrEqual(2);
  });
});

describe("StatsCard indicators", () => {
  test("renders Bearish indicator for MACD when value < 0", () => {
    const crypto = {
      stats: {
        macd: -0.5,
        marketCap: 1000000000,
        volume: 50000000,
        ema: 200,
        rsi: 50,
        sentiment: 50,
      },
    };

    render(<StatsCard crypto={crypto} />);

    const macdBadge = screen.getByTestId("macd-indicator");
    expect(macdBadge).toHaveTextContent("Bearish");
    expect(macdBadge).toHaveClass("bg-red-100", "text-red-800");
  });

  test("renders Oversold indicator for RSI when value <= 30", () => {
    const crypto = {
      stats: {
        macd: 0,
        marketCap: 1000000000,
        volume: 50000000,
        ema: 200,
        rsi: 30,
        sentiment: 50,
      },
    };
  
    render(<StatsCard crypto={crypto} />);
  
    const showMoreBtn = screen.getByRole("button", { name: /show more/i });
    fireEvent.click(showMoreBtn);
  
    const rsiIndicator = screen.getByTestId("rsi-indicator");
    expect(rsiIndicator).toHaveTextContent("Oversold");
    expect(rsiIndicator).toHaveClass("bg-blue-100", "text-blue-800");
  });

  test("renders Bearish indicator for Sentiment when value <= 40", () => {
    const crypto = {
      stats: {
        macd: 0,
        marketCap: 1000000000,
        volume: 50000000,
        ema: 200,
        rsi: 50,
        sentiment: 30,
      },
    };
  
    render(<StatsCard crypto={crypto} />);
  
    const showMoreButton = screen.getByRole("button", { name: /show more/i });
    fireEvent.click(showMoreButton);
  
    const sentimentBadge = screen.getByTestId("sentiment-indicator");
    expect(sentimentBadge).toHaveTextContent("Bearish");
    expect(sentimentBadge).toHaveClass("bg-red-100", "text-red-800");
  });
});
