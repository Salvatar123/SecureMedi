"""README for Dashboard v2.0"""

# SecureMedi Dashboard v2.0

Modern, responsive health monitoring dashboard built with **Next.js** and **FastAPI**.

## Quick Start

```bash
# Backend
cd backend && python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Visit: http://localhost:3000

## Features

### Dashboard
- 🔴 Real-time vital signs (Heart Rate, Temperature, SpO₂)
- 📊 Interactive health trend charts
- 🚨 Alert system with severity levels
- 📈 Health statistics overview
- 📱 Fully responsive design

### Authentication
- 🔐 Doctor login with wallet address
- 🔐 Patient login with credentials
- 🔑 Key-based access control
- ✅ JWT token management

### Data Management
- 📋 Patient record access (doctors only)
- 📥 Export vitals to CSV
- 📌 Access audit logs
- 🔒 Secure blockchain integration

### UI/UX
- 🌙 Dark theme with modern gradients
- ⚡ Smooth animations
- 🎨 Status-based color coding
- 📱 Mobile responsive

## Project Structure

```
SecureMedi/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
│
├── frontend/                   # Next.js frontend
│   ├── pages/                # App pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities & API client
│   ├── types/                # TypeScript types
│   ├── styles/               # Global styles
│   └── package.json
│
└── documentation/
    └── DASHBOARD_V2_SETUP.md
```

## Key Improvements from v1.0

| Feature | v1.0 (Streamlit) | v2.0 (Next.js) |
|---------|------------------|----------------|
| Performance | Medium | Fast ⚡ |
| Customization | Limited | Full ✅ |
| Mobile | Basic | Full responsive 📱 |
| Real-time | 2s polling | 5s polling (WebSocket coming) |
| Charts | Streamlit charts | Recharts interactive 📈 |
| Styling | Basic | Modern design 🎨 |
| Type safety | None | TypeScript ✅ |
| Scalability | Single server | Separate frontend/backend |

## Environment Variables

### Backend (.env)
```
BLOCKCHAIN_RPC_URL=http://localhost:8545
CONTRACT_ADDRESS=0x...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SecureMedi
```

## API Endpoints

### Base URL: `http://localhost:8000`

**Auth**
```
POST   /api/auth/login/doctor
POST   /api/auth/login/patient
POST   /api/auth/verify
```

**Health**
```
GET    /api/health/vitals/latest
GET    /api/health/vitals/history
GET    /api/health/statistics
GET    /api/health/alerts
POST   /api/health/vitals
```

**Patients**
```
GET    /api/patients/{patient_id}
GET    /api/patients/{patient_id}/vitals
POST   /api/patients/{patient_id}/export
```

**Doctors**
```
GET    /api/doctors/{address}
GET    /api/doctors/{address}/access-logs
POST   /api/doctors/{address}/access-patient/{patient_id}
```

See full API docs at: http://localhost:8000/docs

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev              # Dev mode
npm run build            # Production build
npm run type-check       # TypeScript validation
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Docker setup
- Production environment
- Kubernetes deployment
- SSL/TLS configuration

## Troubleshooting

**Q: Frontend can't connect to backend?**
A: Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches backend URL

**Q: Port already in use?**
A: Change port in `.env` files or kill existing process

**Q: TypeScript errors?**
A: Run `npm run type-check` and update `/types/index.ts`

## License

SecureMedi © 2026 - Secure Medical Data Platform

## Support

For issues or questions, check:
- [DASHBOARD_V2_SETUP.md](./DASHBOARD_V2_SETUP.md)
- Backend API docs: http://localhost:8000/docs
