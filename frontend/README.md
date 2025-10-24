# QA Agent Frontend

Modern React-based web interface for QA automation using multi-AI providers.

## Quick Start

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production
```bash
npm run build
```

## Features

- **Dashboard**: Real-time monitoring and metrics
- **Sessions**: Manage QA automation sessions with natural language commands
- **Browser Use**: Quick one-off browser automation tasks
- **Test Results**: View and analyze test execution history
- **WebSocket Support**: Real-time updates during test execution

## Environment

The frontend expects the backend API to be running on:
- Development: http://localhost:8000
- Production: Configure in `vite.config.js`

## Technology

- React 18
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Axios

See main `FRONTEND_GUIDE.md` for detailed documentation.
