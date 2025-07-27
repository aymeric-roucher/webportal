# Webportal Frontend

React frontend for the Webportal website-to-API documentation converter.

## Features

- **Landing Page**: Clean, focused homepage with feature overview
- **URL Input Screen**: Website conversion interface with real-time cache checking
- **Live Processing Dashboard**: Real-time progress tracking with screenshot carousel
- **Results Screen**: Markdown preview and download functionality
- **User Dashboard**: Job management, credits, and account settings
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Real-time Updates**: WebSocket integration via Supabase

## Tech Stack

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand + React Query
- **Routing**: React Router v6
- **Real-time**: Supabase (auth, database, real-time subscriptions)
- **Forms**: React Hook Form + Zod validation

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp src/.env.example .env.local
   ```
   Fill in your Supabase credentials and API URL.

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/
│   ├── ui/           # shadcn/ui components
│   ├── layout/       # Header, Footer, Layout
│   ├── processing/   # Processing-specific components
│   ├── dashboard/    # Dashboard components
│   └── landing/      # Landing page components
├── pages/
│   ├── LandingPage.tsx
│   ├── ConvertPage.tsx
│   ├── ProcessingPage.tsx
│   ├── ResultsPage.tsx
│   └── DashboardPage.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useJobs.ts
│   └── useCachedSites.ts
├── stores/
│   └── useJobStore.ts
├── utils/
│   ├── supabase.ts
│   └── cn.ts
└── types/
    └── index.ts
```

## Key Components

### Landing Page
- Hero section with value proposition
- Feature overview cards
- Demo video placeholder
- Popular sites showcase
- CTA sections

### Convert Page
- URL input with validation
- Cache checking with instant feedback
- Optional interaction instructions
- Popular site quick-select buttons

### Processing Page
- Real-time progress tracking
- Live screenshot carousel
- Step-by-step progress indicators
- Cancel functionality
- WebSocket updates

### Results Page
- Markdown preview and raw view
- Download functionality
- Export options (Postman, OpenAPI)
- Share functionality
- Next steps guidance

### Dashboard
- Account overview with stats
- Job history with search/filter
- Public cache browser
- Account settings and billing

## Environment Variables

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

## Deployment

The frontend is designed to be deployed on platforms like:
- Vercel (recommended)
- Netlify
- Lovable
- Any static hosting service

Make sure to:
1. Set environment variables in your deployment platform
2. Configure your Supabase project for the production domain
3. Update CORS settings for your API backend

## Integration with Backend

The frontend expects the Python FastAPI backend to be running with these endpoints:

- `POST /api/process-website` - Start website processing
- `GET /api/jobs/{jobId}/status` - Get job status
- `GET /api/jobs/{jobId}/results` - Download results
- `GET /api/check-cache/{domain}` - Check if site is cached
- `POST /api/jobs/{jobId}/cancel` - Cancel processing

## Real-time Features

Uses Supabase real-time subscriptions for:
- Live job status updates
- Progress tracking
- Screenshot updates
- Cross-tab synchronization

## Contributing

1. Follow the existing code style
2. Use TypeScript strictly
3. Add proper error handling
4. Test responsive design
5. Update this README for new features