# Daftar Frontend

> A modern, accessible React SPA for the Daftar platform -- extracting handwritten manufacturing reports.

---

## Features

| Page | Route | Description |
|------|-------|-------------|
| Manufacturing Analysis | `/daftar/:section` | Upload images of manufacturing reports (Foam, Sewing, Packing, Shoes) and get real-time OCR extraction via SSE streaming |
| Login | `/login` | JWT-based authentication |
| Register | `/register` | Account creation with email verification |
| Verify Email | `/verify-email` | Email verification flow |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| React 19 | Component library with hooks |
| TypeScript | Type-safe codebase |
| Vite | Fast build tool with HMR |
| Tailwind CSS 4 | Utility-first styling |
| React Router v7 | Client-side routing with protected routes |
| TanStack Query | Server state management and caching |
| Zustand | Client state management (auth, settings, quota, toast) |
| Axios | HTTP client with interceptors |
| React Aria Components | Accessible UI primitives (WAI-ARIA compliant) |
| lucide-react | SVG icon library |

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and **pnpm**
- Running Daftar API backend (see [root README](../README.md))

### Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The dev server runs at **http://localhost:5877** with hot module replacement.

> **Tip:** Use `bash dev.sh` from the project root to start both backend and frontend simultaneously.

### Environment Variables

Create a `.env` file (optional -- defaults work for local development):

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Daftar API base URL | `http://localhost:8101/api/v1` |

### Build for Production

```bash
pnpm build
```

Output is generated in the `dist/` directory, ready to be served by Nginx or any static file server.

### Docker

```bash
docker build -t daftar-frontend .
docker run -p 80:80 daftar-frontend
```

---

## Project Structure

```
frontend/
├── src/
│   ├── api/                  # API client modules
│   ├── components/
│   │   ├── ui/               # Reusable UI primitives
│   │   └── layout/           # App layout (Sidebar, MainLayout)
│   ├── pages/
│   │   ├── PrescriptionPage.tsx    # OCR analysis with real-time progress
│   │   ├── LoginPage.tsx           # User authentication
│   │   ├── RegisterPage.tsx        # Account creation
│   │   └── VerifyEmailPage.tsx     # Email verification
│   ├── stores/
│   │   ├── authStore.ts      # JWT token + user state (persisted)
│   │   ├── settingsStore.ts  # API URL + preferences (persisted)
│   │   ├── quotaStore.ts     # Daily usage tracking
│   │   └── toastStore.ts     # Toast notification state
│   └── utils/                # Shared utility functions
├── public/                   # Static assets
├── index.html                # App shell
├── vite.config.ts            # Vite configuration
└── tsconfig.json             # TypeScript configuration
```

---

## API Integration

The frontend communicates with the Daftar API via Axios. All data routes require JWT authentication.

### Authentication Flow

```
Register -> Verify Email -> Login -> Store JWT -> Attach to all API requests
```

---

## Responsive Design

The frontend is fully responsive with:

- **Mobile sidebar**: Hamburger menu with backdrop overlay
- **Adaptive layouts**: Components reflow for small screens
- **Touch-friendly**: Appropriately sized tap targets

---

## License

Same as the main Daftar project -- see [LICENCE](../LICENCE).
