# DAGRun Status Viewer

A web interface for viewing the status of DAG (Directed Acyclic Graph) runs in the Bluelabel Autopilot system.

## Features

- View detailed status of DAG runs
- Track individual step execution
- See timestamps and durations
- Monitor retry counts and errors
- Responsive design for all screen sizes

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. Open [http://localhost:3000/dag/example-run-id](http://localhost:3000/dag/example-run-id) in your browser

## Environment Variables

Create a `.env.local` file in the root of this directory with the following variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
# Add other environment variables as needed
```

## Project Structure

- `components/` - Reusable React components
  - `DAGRunStatus.tsx` - Main component for displaying DAG run status
- `pages/` - Next.js pages
  - `dag/[runId].tsx` - DAG run details page
- `lib/` - Utility functions and types
  - `types.ts` - TypeScript type definitions for DAG runs and steps

## Development

- Use TypeScript for type safety
- Follow the [Next.js](https://nextjs.org/docs) and [React](https://reactjs.org/docs/getting-started.html) documentation
- Write tests for new components and utilities
- Use [Tailwind CSS](https://tailwindcss.com/docs) for styling

## Testing

Run the test suite:

```bash
npm test
# or
yarn test
```

## Building for Production

```bash
npm run build
# or
yarn build
```

## Deployment

This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/api-reference/create-next-app).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
