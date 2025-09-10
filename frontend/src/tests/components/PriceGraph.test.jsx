// PriceGraph.test.jsx
import { render, screen } from '@testing-library/react';
import React from 'react';

import PriceGraph from '../../components/PriceGraph';

// Mock recharts so we can test render logic without actual chart rendering complexity
jest.mock('recharts', () => {
  const Original = jest.requireActual('recharts');

  // Create simple mock components
  const MockComponent = (name) => (props) => (
    <div data-testid={name} {...props} />
  );

  return {
    ...Original,
    ResponsiveContainer: MockComponent('ResponsiveContainer'),
    LineChart: MockComponent('LineChart'),
    CartesianGrid: MockComponent('CartesianGrid'),
    XAxis: MockComponent('XAxis'),
    YAxis: MockComponent('YAxis'),
    Tooltip: MockComponent('Tooltip'),
    Line: MockComponent('Line'),
  };
});

describe('PriceGraph', () => {
  const mockData = [
    { timestamp: 1620000000000, price: 100 },
    { timestamp: 1620003600000, price: 105 },
  ];
  const mockFormatLabel = jest.fn((ts) => `Formatted ${ts}`);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the container', () => {
    render(<PriceGraph data={mockData} formatLabel={mockFormatLabel} />);

    expect(
      screen.getByTestId('recharts-responsive-container')
    ).toBeInTheDocument();
  });

  test('passes data to the LineChart', () => {
    render(<PriceGraph data={mockData} formatLabel={mockFormatLabel} />);

    const lineChart = screen.getByTestId('LineChart');
    expect(lineChart).toHaveAttribute('data', expect.anything());
  });

  test('renders XAxis and YAxis components', () => {
    render(<PriceGraph data={mockData} formatLabel={mockFormatLabel} />);

    expect(screen.getByTestId('XAxis')).toBeInTheDocument();
    expect(screen.getByTestId('YAxis')).toBeInTheDocument();
  });

  test('renders Tooltip and Line components', () => {
    render(<PriceGraph data={mockData} formatLabel={mockFormatLabel} />);

    expect(screen.getByTestId('Tooltip')).toBeInTheDocument();
    expect(screen.getByTestId('Line')).toBeInTheDocument();
  });

  test('calls formatLabel function for XAxis and Tooltip', () => {
    render(<PriceGraph data={mockData} formatLabel={mockFormatLabel} />);

    expect(screen.getByTestId('XAxis').getAttribute('tickFormatter')).toBeDefined();
    expect(screen.getByTestId('Tooltip').getAttribute('labelFormatter')).toBeDefined();
  });
});
