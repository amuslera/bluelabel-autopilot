// Simple mock for next/router
const useRouter = jest.fn();
const push = jest.fn().mockResolvedValue(true);
const replace = jest.fn().mockResolvedValue(true);
const prefetch = jest.fn().mockResolvedValue(undefined);

const mockRouter = {
  route: '/',
  pathname: '/',
  query: {},
  asPath: '/',
  push,
  replace,
  prefetch,
  back: jest.fn(),
  reload: jest.fn(),
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
};

useRouter.mockReturnValue(mockRouter);

const withRouter = (Component) => {
  return function WithRouter(props) {
    return <Component {...props} router={mockRouter} />;
  };
};

module.exports = {
  __esModule: true,
  useRouter,
  withRouter,
  Router: mockRouter,
};
