const useRouter = () => ({
  route: '/',
  pathname: '/',
  query: {},
  asPath: '/',
  push: jest.fn(),
  replace: jest.fn(),
  back: jest.fn(),
  prefetch: jest.fn(),
  beforePopState: jest.fn(),
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
});

module.exports = {
  useRouter,
  withRouter: (component) => component,
  Router: {
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  },
  __esModule: true,
};
