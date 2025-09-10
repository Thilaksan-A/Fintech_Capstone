import { fireEvent, render, screen, within } from '@testing-library/react';

import '@testing-library/jest-dom';
import { PurchasePlatformsList } from '../../components/PurchasePlatformsList';

// Mock lucide-react icons and shadcn components
jest.mock('lucide-react', () => ({
  ShoppingCart: () => <div data-testid="shopping-cart-icon">🛒</div>,
  ExternalLink: () => <div data-testid="external-link-icon">🔗</div>,
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, ...props }) => <button {...props}>{children}</button>,
}));

// Corrected Dialog mock to conditionally render its content
jest.mock('@/components/ui/dialog', () => ({
  Dialog: ({ children, open, onOpenChange }) => (
    <div data-testid="mock-dialog" data-open={open}>
      {children}
      {open && (
        <div data-testid="dialog-content-container">
          {children.find(c => c.type && c.type.name === 'DialogContent')}
        </div>
      )}
    </div>
  ),
  DialogTrigger: ({ children }) => <div data-testid="dialog-trigger">{children}</div>,
  DialogContent: ({ children }) => <div data-testid="dialog-content">{children}</div>,
  DialogHeader: ({ children }) => <div>{children}</div>,
  DialogTitle: ({ children }) => <h2>{children}</h2>,
  DialogDescription: ({ children }) => <p>{children}</p>,
}));

jest.mock('@/components/ui/scroll-area', () => ({
  ScrollArea: ({ children }) => <div data-testid="scroll-area">{children}</div>,
}));

jest.mock('@/components/ui/separator', () => ({
  Separator: () => <hr data-testid="separator" />,
}));

describe('PurchasePlatformsList', () => {
  const name = 'ExampleCoin';

  // Test case for no platforms
  test('renders no platforms message when platforms prop is empty', () => {
    render(<PurchasePlatformsList name={name} platforms={[]} />);
    expect(screen.getByText(`No purchase platforms available for ${name}`)).toBeInTheDocument();
    expect(screen.queryByTestId('shopping-cart-icon')).toBeInTheDocument();
  });

  // Test case for string-based platforms
  test('handles platforms provided as a comma-separated string', () => {
    const platformsString = 'PlatformA, PlatformB, PlatformC';
    render(<PurchasePlatformsList name={name} platforms={platformsString} />);
    expect(screen.getByText('PlatformA')).toBeInTheDocument();
    expect(screen.getByText('PlatformB')).toBeInTheDocument();
    expect(screen.getByText('PlatformC')).toBeInTheDocument();
  });
  
  // Test cases for platforms count <= 3
  test('renders up to 3 platforms directly on the page', () => {
    const platforms = ['PlatformA', 'PlatformB'];
    render(<PurchasePlatformsList name={name} platforms={platforms} />);
    expect(screen.getByText(`You can purchase ${name} on the following platforms:`)).toBeInTheDocument();
    expect(screen.getByText('PlatformA')).toBeInTheDocument();
    expect(screen.getByText('PlatformB')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /view all/i })).not.toBeInTheDocument();
  });

  // Test case for "View All" button click
  test('opens the dialog and shows all platforms when "View All" button is clicked', () => {
    const platforms = ['PlatformA', 'PlatformB', 'PlatformC', 'PlatformD'];
    render(<PurchasePlatformsList name={name} platforms={platforms} />);

    // Mock the open state of the Dialog
    const viewAllButton = screen.getByRole('button', { name: /view all/i });
    fireEvent.click(viewAllButton);

    // Check if the dialog content is rendered with all platforms
    const dialogContent = screen.getByTestId('dialog-content');
    expect(dialogContent).toBeInTheDocument();
    expect(within(dialogContent).getByText(`Where to Buy ${name}`)).toBeInTheDocument();
    expect(within(dialogContent).getByText('PlatformA')).toBeInTheDocument();
    expect(within(dialogContent).getByText('PlatformB')).toBeInTheDocument();
    expect(within(dialogContent).getByText('PlatformC')).toBeInTheDocument();
    expect(within(dialogContent).getByText('PlatformD')).toBeInTheDocument();
  });

  // Test case for the link and URL generation
  test('each platform card links to a correct Google search URL', () => {
    const platforms = ['PlatformA'];
    render(<PurchasePlatformsList name={name} platforms={platforms} />);
    const link = screen.getByRole('link', { name: /search for platforma exchange/i });
    
    // Update the expected href value to match the decoded URL
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://www.google.com/search?q=PlatformA crypto exchange');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  // Test case for the final note
  test('renders the final disclaimer note at the bottom', () => {
    render(<PurchasePlatformsList name={name} platforms={['PlatformA']} />);
    const note = screen.getByText(/links will search for the platform/i);
    expect(note).toBeInTheDocument();
    expect(note).toHaveTextContent('Note: Links will search for the platform. Always verify authenticity and conduct your own research before making purchases.');
  });
});
