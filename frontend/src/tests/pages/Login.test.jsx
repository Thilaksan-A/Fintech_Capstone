import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import Login from '../../pages/Login';

const mockAnimationComplete = jest.fn();
jest.mock('../../components/ui/SplitText', () => (props) => {
  if (props.onLetterAnimationComplete) {
    props.onLetterAnimationComplete();
  }
  return <h1 data-testid="split-text">{props.text}</h1>;
});

jest.mock('@/components/LoginCard', () => () => <div data-testid="login-card">LoginCard</div>);

describe('Login page', () => {
  test('renders logo, heading, login card, and sign up link', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(consoleSpy).toHaveBeenCalledWith('All letters have animated!');

    consoleSpy.mockRestore();

    expect(screen.getByRole('img')).toHaveAttribute('src', '/logo.png');

    expect(screen.getByTestId('split-text')).toHaveTextContent('Welcome to SafeGuard');

    expect(screen.getByTestId('login-card')).toBeInTheDocument();

    const signupButton = screen.getByRole('button', { name: /no account yet\? sign up/i });
    expect(signupButton).toBeInTheDocument();

    const link = signupButton.closest('a');
    expect(link).toHaveAttribute('href', '/signup');
  });
});
