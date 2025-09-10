import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import { ExpertGraph } from "../../components/ExpertGraph";
import '@testing-library/jest-dom';

const mockData = [
  {
    timestamp: "2025-01-01",
    price: 100,
    ema: 102,
    rsi: 45,
    macd: 1.5,
    sentiment: 60,
  },
  {
    timestamp: "2025-01-02",
    price: 110,
    ema: 105,
    rsi: 50,
    macd: 1.2,
    sentiment: 55,
  },
];

const formatLabel = (timestamp) => `Formatted: ${timestamp}`;

describe("ExpertGraph Component", () => {
  beforeAll(() => {
    global.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  });

  test("renders without crashing", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);
    expect(screen.getByText("Technical Indicators")).toBeInTheDocument();
  });

  test("initially shows 0 active indicators", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);
    expect(screen.getByText("0 active")).toBeInTheDocument();
  });

  test("toggles RSI indicator", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);

    const rsiButton = screen.getByText("RSI").closest("button");
    expect(rsiButton).toBeInTheDocument();

    fireEvent.click(rsiButton);
    expect(screen.getByText("1 active")).toBeInTheDocument();
    expect(screen.getByText("Relative Strength Index")).toBeInTheDocument();

    // toggle off
    fireEvent.click(rsiButton);
    expect(screen.getByText("0 active")).toBeInTheDocument();
  });

  test("toggles multiple indicators", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);

    fireEvent.click(screen.getByText("RSI").closest("button"));
    fireEvent.click(screen.getByText("EMA").closest("button"));
    fireEvent.click(screen.getByText("MACD").closest("button"));

    expect(screen.getByText("3 active")).toBeInTheDocument();
    expect(screen.getByText("Relative Strength Index")).toBeInTheDocument();
    expect(screen.getByText("Exponential Moving Average")).toBeInTheDocument();
    expect(screen.getByText("Moving Average Convergence Divergence")).toBeInTheDocument();
  });

  test("shows tooltip when active (custom rendering)", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);

    const chartContainer = screen.getAllByTestId("custom-tooltip")[0];
    expect(chartContainer).toBeInTheDocument();
  });

  test("indicator button styles change on toggle", () => {
    render(<ExpertGraph data={mockData} formatLabel={formatLabel} />);
    const emaButton = screen.getByText("EMA").closest("button");

    expect(emaButton).toHaveClass("hover:bg-muted");
    fireEvent.click(emaButton);
    expect(emaButton).toHaveClass("bg-red-100", "text-red-600");
  });
});

// Dummy getSigFig to match your logic (or import from component if possible)
const getSigFig = (val) => {
  if (val) {
    return val.toPrecision(4);
  }
  return null;
};

describe('ExpertGraph component conditional outputs', () => {
  const baseData = {
    price: 100,
    ema: 1234.5678,
    rsi: 45.6789,
    macd: 0.123456,
    sentiment: 78.9012,
  };

  beforeAll(() => {
    global.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  });

  test('renders EMA when showEMA is true', () => {
    const formatLabel = (val) => val;
    render(<ExpertGraph data={baseData} formatLabel={formatLabel} />);
    const sentimentToggle = screen.getByRole('button', { name: /EMA/i });
    fireEvent.click(sentimentToggle);
    expect(sentimentToggle).not.toHaveClass('hover:bg-muted');  
  });

  test('does not render EMA when showEMA is false', () => {
    render(<ExpertGraph data={baseData} showEMA={false} />);
    expect(screen.queryByTestId('formatted-ema')).toBeNull();
  });

  test('renders RSI when showRSI is true', () => {
    const formatLabel = (val) => val;
    render(<ExpertGraph data={baseData} formatLabel={formatLabel} />);
    const sentimentToggle = screen.getByRole('button', { name: /RSI/i });
    fireEvent.click(sentimentToggle);
    expect(sentimentToggle).not.toHaveClass('hover:bg-muted');  
  });

  test('renders MACD when showMACD is true', () => {
    const formatLabel = (val) => val;
    render(<ExpertGraph data={baseData} formatLabel={formatLabel} />);
    const sentimentToggle = screen.getByRole('button', { name: /MACD/i });
    fireEvent.click(sentimentToggle);
    expect(sentimentToggle).not.toHaveClass('hover:bg-muted');  
  });

  test('renders Sentiment when showSentiment is true', () => {
    const formatLabel = (val) => val;
    render(<ExpertGraph data={baseData} formatLabel={formatLabel} />);
    const sentimentToggle = screen.getByRole('button', { name: /Sentiment/i });
    fireEvent.click(sentimentToggle);
    expect(sentimentToggle).not.toHaveClass('hover:bg-muted');  
  });
});
