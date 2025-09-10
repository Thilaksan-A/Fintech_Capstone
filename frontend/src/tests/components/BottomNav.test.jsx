import { render, screen } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';

import BottomNav from '../../components/BottomNav';

import '@testing-library/jest-dom';

describe('BottomNav', () => {
  const renderWithRouter = (ui) => {
    return render(<MemoryRouter>{ui}</MemoryRouter>);
  };

  test('renders BottomNav component', () => {
    renderWithRouter(<BottomNav />);
    
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  test('renders all navigation links with labels', () => {
    renderWithRouter(<BottomNav />);

    expect(screen.getByText('News')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  test('links point to correct routes', () => {
    renderWithRouter(<BottomNav />);

    expect(screen.getByText('News').closest('a')).toHaveAttribute('href', '/news');
    expect(screen.getByText('Home').closest('a')).toHaveAttribute('href', '/');
    expect(screen.getByText('Profile').closest('a')).toHaveAttribute('href', '/profile');
  });

  test('renders Lucide icons', () => {
    const { container } = renderWithRouter(<BottomNav />);
  
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThanOrEqual(3);
  });
});
