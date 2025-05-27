const { render, screen } = require('@testing-library/react');
require('@testing-library/jest-dom');

const React = require('react');

const Hello = ({ name }) => {
  return /*#__PURE__*/React.createElement("div", null, "Hello, ", name, "!");
};

describe('Hello Component', () => {
  it('renders the greeting with the provided name', () => {
    render(/*#__PURE__*/React.createElement(Hello, { name: "World" }));
    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
  });
});
