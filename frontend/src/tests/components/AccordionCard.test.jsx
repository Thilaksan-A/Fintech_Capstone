import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import { AccordionCard } from '../../components/AccordionCard';

describe('AccordionCard', () => {
  test('toggles content on click', async () => {
    render(
      <AccordionCard
        title="Accordion Title"
        content={<p>Accordion Content</p>}
        icon={<span aria-label="icon" role="img"></span>}
      />
    );

    const button = screen.getByRole('button', { name: /Accordion Title/i });
    expect(button).toBeInTheDocument();
    
    expect(screen.queryByText('Accordion Content')).not.toBeInTheDocument();

    await userEvent.click(button);
    expect(screen.getByText('Accordion Content')).toBeInTheDocument();

    await userEvent.click(button);
    expect(screen.queryByText('Accordion Content')).not.toBeInTheDocument();
  });
});
