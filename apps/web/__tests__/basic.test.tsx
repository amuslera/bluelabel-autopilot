import React from 'react';
import { render, screen } from '@testing-library/react';

describe('Basic Test', () => {
  it('renders a simple component', () => {
    render(<div data-testid="test-element">Hello, World!</div>);
    const element = screen.getByTestId('test-element');
    expect(element).toBeInTheDocument();
    expect(element).toHaveTextContent('Hello, World!');
  });

  it('performs a simple calculation', () => {
    expect(1 + 1).toBe(2);
  });
});
