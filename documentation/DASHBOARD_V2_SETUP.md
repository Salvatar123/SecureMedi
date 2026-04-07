"""
# SecureMedi Dashboard v2.0 Setup Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + React)                │
│                   (:3000)                                     │
│  - Login page                                               │
│  - Real-time dashboard with charts                           │
│  - Patient management                                        │
│  - Doctor access logs                                        │
└────────────────────┬────────────────────────────────────────┘
                     │ (HTTP/WebSocket)
┌────────────────────▼────────────────────────────────────────┐
│         Backend API (FastAPI)                                │
│                   (:8000)                                     │
│  - Authentication & Authorization                            │
│  - Health data endpoints                                     │
│  - Patient records                                           │
│  - Doctor operations                                         │
│  - Blockchain integration                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Python Core Services                                 │
│  - BlockchainConnector (Web3)                                │
│  - LoggerService (CSV)                                       │
│  - DetectorService (Anomaly detection)                       │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Backend Setup

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Create .env file (copy from root)
cp ../.env .env

# 3. Run backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Install frontend dependencies
cd frontend
npm install

# 2. Frontend will use NEXT_PUBLIC_API_URL from .env.local
# (Already configured to http://localhost:8000)

# 3. Run frontend
npm run dev
# Open http://localhost:3000
```

## Running the Full Stack

### Option 1: Separate Terminals

** Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Using Docker (Coming Soon)

## API Endpoints

### Authentication
- `POST /api/auth/login/doctor` - Doctor login
- `POST /api/auth/login/patient` - Patient login
- `POST /api/auth/verify` - Verify token
- `POST /api/auth/logout` - Logout

### Health Monitoring
- `GET /api/health/vitals/latest` - Latest vital signs
- `GET /api/health/vitals/history` - Vitals history
- `GET /api/health/statistics` - Health stats
- `GET /api/health/alerts` - Active alerts
- `POST /api/health/vitals` - Log new vitals

### Patient Management
- `GET /api/patients/{patient_id}` - Patient record
- `GET /api/patients/{patient_id}/vitals` - Patient vitals
- `POST /api/patients/{patient_id}/export` - Export data

### Doctor Operations
- `GET /api/doctors/{address}` - Doctor info
- `GET /api/doctors/{address}/access-logs` - Access logs
- `POST /api/doctors/{address}/access-patient/{patient_id}` - Log access

## Features by Version

### v2.0 New Features
✅ Modern React dashboard with Tailwind CSS
✅ Real-time health monitoring (5-second refresh)
✅ Interactive charts (Recharts)
✅ Alert system with severity levels
✅ Responsive design (mobile-friendly)
✅ Doctor & Patient portals
✅ Access audit logs
✅ Health statistics
✅ Data export functionality
✅ Dark theme

### Coming in v2.1
- WebSocket real-time updates
- Historical data analytics
- Predictive alerts
- Admin dashboard
- Multi-language support

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Pydantic** - Data validation
- **Web3.py** - Blockchain integration
- **Python 3.9+**

### Frontend
- **Next.js 14** - React framework
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Charts & visualization
- **Zustand** - State management
- **Axios** - HTTP client
- **Heroicons** - Icon library

## Development Guidelines

### Backend
- All routes are in `/app/api/`
- Service layer in `/app/services/`
- Data models in `/app/models/`
- Add CORS for new frontend URLs

### Frontend
- Components in `/components/`
- Pages in `/pages/`
- Types in `/types/`
- API client in `/lib/api.ts`
- Auth store in `/lib/auth.ts`

## Troubleshooting

### CORS Issues
- Add frontend URL to `app.add_middleware(CORSMiddleware, ...)` in backend/app/main.py

### API Connection Failed
- Check backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local

### TypeScript Errors
- Run `npm run type-check` to verify
- Update types in `/types/index.ts`

## Next Steps

1. Set up backend services properly
2. Integrate WebSocket for real-time updates
3. Implement admin dashboard
4. Add more analytics and forecasting
5. Deploy with Docker Compose

See [DEPLOYMENT.md](../documentation/DEPLOYMENT.md) for production setup.
"""
