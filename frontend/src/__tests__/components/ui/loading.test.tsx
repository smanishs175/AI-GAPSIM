// @ts-nocheck
import React from 'react';
import { render, screen } from '@testing-library/react';
import Loading from '@/components/ui/loading';

describe('Loading component', () => {
  it('renders the loading spinner and text', () => {
    render(<Loading />);

    // Check if the loading text is rendered
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Check if the spinner is rendered (by class)
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });
});
