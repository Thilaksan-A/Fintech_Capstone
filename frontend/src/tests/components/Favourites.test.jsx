import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';

import { Favourites } from '../../components/Favourites';


// Mock WatchlistStarButton
jest.mock('@/components/WatchlistStarButton', () => ({
  WatchlistStarButton: ({ symbol, isWatched, onToggle }) => (
    <button data-testid={`star-${symbol}`} onClick={() => onToggle(symbol)}>
      {isWatched ? '★' : '☆'}
    </button>
  ),
}));

const renderWithRouter = (ui) => {
  return render(<Router>{ui}</Router>);
};

describe('Favourites component', () => {
  const sampleCoins = [
    {
      symbol: 'BTC',
      name: 'Bitcoin',
      image: 'btc.png',
      price: 30000,
      priceUp: true,
    },
    {
      symbol: 'ETH',
      name: 'Ethereum',
      image: 'eth.png',
      price: 1800,
      priceUp: false,
    },
  ];

  test('renders "No favourites" message when list is empty', () => {
    renderWithRouter(<Favourites favourites={[]} watchlistState={new Set()} onToggle={jest.fn()} />);
    expect(screen.getByText('No favourites added yet.')).toBeInTheDocument();
  });

  test('renders a list of favourite coins', () => {
    renderWithRouter(
      <Favourites favourites={sampleCoins} watchlistState={new Set(['BTC'])} onToggle={jest.fn()} />
    );

    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('Bitcoin')).toBeInTheDocument();
    expect(screen.getByText('ETH')).toBeInTheDocument();
    expect(screen.getByText('Ethereum')).toBeInTheDocument();
  });

  test('displays price with correct direction (↑ / ↓)', () => {
    renderWithRouter(
      <Favourites favourites={sampleCoins} watchlistState={new Set()} onToggle={jest.fn()} />
    );

    expect(screen.getByText('$30000 ↑')).toBeInTheDocument();
    expect(screen.getByText('$1800 ↓')).toBeInTheDocument();

    expect(screen.getByText('$30000 ↑')).toHaveClass('text-green-600');
    expect(screen.getByText('$1800 ↓')).toHaveClass('text-red-600');
  });

  test('calls onToggle when WatchlistStarButton is clicked', () => {
    const onToggleMock = jest.fn();
    renderWithRouter(
      <Favourites favourites={sampleCoins} watchlistState={new Set()} onToggle={onToggleMock} />
    );

    const starButton = screen.getByTestId('star-BTC');
    fireEvent.click(starButton);

    expect(onToggleMock).toHaveBeenCalledWith('BTC');
  });
});
