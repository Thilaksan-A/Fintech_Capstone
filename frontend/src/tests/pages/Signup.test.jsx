import { render, screen } from '@testing-library/react';

import Signup from '../../pages/Signup';

jest.mock('@/components/SignupCard', () => (props) => (
  <div data-testid="signup-card">{props.onSuccess ? 'has onSuccess' : 'no onSuccess'}</div>
));

jest.mock('react-fast-marquee', () => (props) => (
  <div data-testid="marquee" className={props.className}>{props.children}</div>
));

describe('Signup page', () => {
  test('renders marquee with correct text and SignupCard with onSuccess prop', () => {
    const mockOnSuccess = jest.fn();

    render(<Signup onSuccess={mockOnSuccess} />);

    const marquee = screen.getByTestId('marquee');
    expect(marquee).toBeInTheDocument();
    expect(marquee).toHaveClass('absolute');
    expect(marquee).toHaveTextContent(/crypto made easy +/i);

    const signupCard = screen.getByTestId('signup-card');
    expect(signupCard).toBeInTheDocument();
    expect(signupCard).toHaveTextContent('has onSuccess');
  });
});
