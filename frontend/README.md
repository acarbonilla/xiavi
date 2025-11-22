# XiAv Speech AI - Frontend

Next.js frontend for the AI-powered interview platform.

## 🚀 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Context API

## 📋 Prerequisites

- Node.js 18+
- Backend API running on `http://localhost:8000`

## 🔧 Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with AuthProvider
│   ├── page.tsx                # Landing page
│   ├── login/
│   │   └── page.tsx           # Login page
│   ├── register/
│   │   └── page.tsx           # Registration page
│   ├── dashboard/             # Applicant dashboard (coming soon)
│   ├── hr-dashboard/          # HR dashboard (coming soon)
│   ├── interview/             # Interview interface (coming soon)
│   ├── training/              # Training center (coming soon)
│   └── globals.css            # Global styles
├── components/                # Reusable components (coming soon)
├── lib/
│   ├── api.ts                 # API client with JWT auth
│   ├── auth.tsx               # Authentication context
│   └── utils.ts               # Utility functions
├── types/
│   └── index.ts               # TypeScript interfaces
└── tailwind.config.ts         # Tailwind configuration
```

## 🎨 Features Implemented

### ✅ Authentication System
- **Login Page**: JWT-based authentication with error handling
- **Register Page**: User registration with role selection (Applicant/HR)
- **Auth Context**: Global authentication state management
- **Token Management**: Automatic token refresh and storage

### ✅ Landing Page
- Hero section with gradient design
- Feature showcase
- How it works section
- Call-to-action sections
- Responsive navigation

### ✅ API Integration
- Complete API client with all backend endpoints
- JWT token interceptors
- Automatic token refresh on 401 errors
- Type-safe API methods

### ✅ UI Components
- Custom Tailwind components (buttons, inputs, cards, badges)
- Responsive design
- Smooth animations and transitions
- Beautiful gradient designs

## 🎯 Pages

### Landing Page (`/`)
- Hero section with call-to-action
- Feature highlights
- How it works flow
- Footer

### Login Page (`/login`)
- Username/password authentication
- Error handling
- Redirect based on user role

### Register Page (`/register`)
- Role selection (Applicant/HR)
- Multi-field registration form
- Password confirmation
- Success state with redirect

## 🔐 Authentication Flow

1. User registers or logs in
2. Backend returns JWT access and refresh tokens
3. Tokens stored in localStorage
4. API client automatically adds Bearer token to requests
5. On 401 error, automatically refreshes token
6. On refresh failure, redirects to login

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (#0ea5e9 to #0369a1)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Error**: Red (#ef4444)

### Components
- `.btn-primary`: Primary action button
- `.btn-secondary`: Secondary button
- `.btn-outline`: Outlined button
- `.input-field`: Form input field
- `.card`: Card container
- `.badge`: Status badge

## 📝 Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🔗 API Endpoints Used

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile

## 🚧 Coming Soon

- Applicant Dashboard
- HR Dashboard
- Interview Interface with Video Recording
- Training Center
- Results and Evaluation Pages
- Real-time Transcript Viewer
- Video Player Component

## 🎓 Key Features

### Type Safety
- Full TypeScript coverage
- Comprehensive type definitions for all API models
- Type-safe API client methods

### Authentication
- JWT-based authentication
- Automatic token refresh
- Role-based routing
- Protected routes

### UI/UX
- Modern, clean design
- Smooth animations
- Responsive layout
- Accessible components

## 📚 Dependencies

```json
{
  "react": "^19.0.0",
  "next": "^15.1.4",
  "axios": "^1.6.5",
  "lucide-react": "^0.460.0",
  "tailwindcss": "^3.4.1"
}
```

## 🤝 Contributing

The frontend is built with modern React patterns:
- Client components for interactivity
- Server components for static content
- React hooks for state management
- Context API for global state

## 📄 License

MIT License
