// Add any necessary polyfills for the test environment
if (typeof globalThis.URL.createObjectURL === 'undefined') {
  Object.defineProperty(globalThis.URL, 'createObjectURL', {
    value: jest.fn(),
  });
}

// Add any other necessary polyfills here
