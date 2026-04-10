# Plan: Secure SecureMedi with Full Auth & Audit Layer

## TL;DR
Transform SecureMedi from an unprotected prototype to a production-ready healthcare app with proper JWT authentication, role-based access control, audit logging, and secure data storage. Implement in 5 phases: (1) JWT auth + middleware, (2) RBAC enforcement, (3) audit & logging infrastructure, (4) frontend security, (5) database & deployment hardening.

---

## Implementation Progress

✅ **PHASE 1 COMPLETE** - JWT Authentication & Token Management
- Created `backend/app/services/jwt_service.py` with RS256 signing
- Updated `backend/app/services/auth_service.py` to use JWT service
- Fixed `verify_patient()` to call blockchain verification
- Updated auth routes: `/login/doctor`, `/login/patient`, `/refresh`, `/verify`, `/logout`
- Added `RefreshRequest` model
- Updated `AuthResponse` to include `refresh_token`
- Backend running successfully on http://127.0.0.1:8000

✅ **PHASE 2 COMPLETE** - Authentication Middleware & RBAC
- Created `backend/app/middleware/auth.py` - JWT extraction + validation
- Created `backend/app/middleware/rbac.py` - RBAC decorators (@require_role, @require_self_or_role)
- Protected all routes:
  * Health routes: `@require_role("DOCTOR", "PATIENT")`
  * Patient routes: `@require_self_or_role("DOCTOR", "ADMIN")`
  * Doctor routes: `@require_role("DOCTOR")`
  * Admin routes: `@require_role("ADMIN")`
- Created `backend/app/api/admin_routes.py` with:
  * POST `/api/admin/users/register` - Register new users
  * GET `/api/admin/users` - List all users
  * GET `/api/admin/users/{address}` - Get user details
  * PATCH `/api/admin/users/{address}/role` - Change user role
  * DELETE `/api/admin/users/{address}` - Deactivate user
  * GET `/api/admin/stats` - System statistics
- Registered `AuthenticationMiddleware` in `main.py`
- Hardened CORS: only allow specific methods and headers
- All routes now require authentication (except login/refresh/request-key)
- Backend running with RBAC enforced ✅

## Steps

### PHASE 1: JWT Authentication & Token Management (Days 1-2)

1. **Create JWT Service** (`backend/app/services/jwt_service.py`)
   - Generate JWT tokens with RS256 signature (public/private key pair)
   - Claims: `sub` (user address), `role` (DOCTOR/PATIENT), `exp` (15 min), `iat`, `jti` (token ID for revocation)
   - Implement refresh token pattern (7-day expiration)
   - Token revocation list (in-memory cache with Redis for production)

2. **Replace Custom Token in AuthService**
   - Update `generate_access_token()` to use JWT service
   - Update `verify_token()` to validate JWT signature & expiration
   - Implement `refresh_token()` endpoint

3. **Add Token Revocation**
   - Create `TokenBlacklist` data structure (in-memory dict: jti → expiration_time)
   - Implement `/api/auth/logout` to add token to blacklist
   - Clean up expired tokens periodically

4. **Update Auth Routes** (`backend/app/api/auth_routes.py`)
   - Modify `/login/doctor` and `/login/patient` to use JWT service
   - Add `/api/auth/refresh` endpoint
   - Enhance `/api/auth/logout` with actual token revocation

5. **Fix Patient Authentication** (`backend/app/services/auth_service.py`)
   - Uncomment and fix `verify_patient()` to call blockchain verification
   - Add proper validation (currently stubbed, returns true)

---

### PHASE 2: Authentication Middleware & RBAC (Days 2-3)

1. **Create Auth Middleware** (`backend/app/middleware/auth.py`)
   - Extract JWT from `Authorization: Bearer` header
   - Validate signature, expiration, blacklist status
   - Attach decoded token to `request.state.user` (contains address, role, exp)
   - Return 401 if token missing/invalid

2. **Create RBAC Middleware** (`backend/app/middleware/rbac.py`)
   - Decorator: `@require_role(DOCTOR)` to protect routes
   - Decorator: `@require_permission("read:patient_data")` for fine-grained access
   - Reject 403 Forbidden if role doesn't match

3. **Protect All Routes**
   - `GET /api/health/**` → `@require_role(DOCTOR, PATIENT)`
   - `POST /api/health/**` → `@require_role(DOCTOR)` (only doctors can log vitals for patients)
   - `GET /api/patients/**` → `@require_role(DOCTOR, PATIENT)` (patients can only see own data)
   - `POST /api/doctors/emergency-access` → `@require_role(DOCTOR)`
   - `GET /api/doctors/access-logs` → `@require_role(DOCTOR)` (own logs) or `@require_role(ADMIN)` (all)

4. **Add Admin Routes** (`backend/app/api/admin_routes.py`)
   - `POST /api/admin/users/register` - register new doctors/patients
   - `GET /api/admin/audit-logs` - view all audit logs
   - `DELETE /api/admin/users/{address}` - deactivate users
   - `PATCH /api/admin/users/{address}/role` - change roles

5. **Data Access Control** (`backend/app/services/auth_service.py`)
   - Add `can_access_patient_data(actor_address, actor_role, target_patient_id)` method
   - Doctor can access: own patients, patients from emergency access (with valid key)
   - Patient can access: own data only
   - Admin can access: all

---

### PHASE 3: Audit Logging & Monitoring (Days 3-4)

1. **Create Audit Logger** (`backend/app/services/audit_service.py`)
   - Log all sensitive operations: login, data access, emergency access, token refresh
   - Fields: timestamp, actor_address, actor_role, action, resource_id, result (success/fail), ip_address
   - Forward critical logs to blockchain (AccessLog contract)

2. **Create Middleware for Audit Logging** (`backend/app/middleware/audit.py`)
   - Intercept all requests matching patterns: `/api/health/**`, `/api/patients/**`, `/api/doctors/**`
   - Log request + response (mask sensitive data)
   - Capture response status & errors

3. **Add Audit Routes** (`backend/app/api/audit_routes.py`)
   - `GET /api/audit/my-logs` - user's own activity
   - `GET /api/audit/logs` (admin only) - all audit logs with filtering

4. **Database for Audit Logs** (Phase 5, add placeholder)
   - Replace CSV with PostgreSQL table `audit_logs`
   - Indexed on: timestamp, actor_address, action, resource_id

5. **Structured Logging** (`backend/app/middleware/logging.py`)
   - Replace basic `logging` with structured JSON logs
   - Format: `{"timestamp", "level", "event", "context", "error"}`
   - Send to stdout (container-friendly, can be piped to ELK/Datadog)

---

### PHASE 4: Frontend Security Hardening (Days 4-5)

1. **Create Auth Interceptor** (`frontend/middleware/authMiddleware.ts`)
   - Intercept all API requests
   - Validate token expiration before sending
   - Auto-refresh tokens when close to expiration (< 5 min remaining)
   - Clear auth state on 401 response

2. **Update API Client** (`frontend/lib/api.ts`)
   - Add refresh token logic
   - Add retry mechanism for failed requests (exponential backoff)
   - Sanitize error messages (don't expose stack traces to user)

3. **Secure Token Storage** (`frontend/lib/auth.ts`)
   - Replace plain Zustand store with encrypted local storage
   - Use `crypto-js` for client-side encryption (token + address)
   - Add token expiration checks on app load
   - Clear storage on logout

4. **Route Protection** (`frontend/middleware/protectedRoutes.ts`)
   - Create `ProtectedRoute` component that checks auth state
   - Redirect unauthenticated users to `/login`
   - Redirect patients away from `/request-access` (only doctors)
   - Redirect unauthorized users from `/admin` (only admins)

5. **Input Validation** (`frontend/lib/validators.ts`)
   - Validate all form inputs before submission
   - Patient ID format, wallet address format, access key format
   - Show real-time validation feedback

6. **Security Headers** (`frontend/next.config.js`)
   - Add CSP (Content Security Policy) headers
   - Add X-Frame-Options: DENY
   - Add X-Content-Type-Options: nosniff
   - Add Strict-Transport-Security (HSTS)

7. **Encrypt Sensitive Data in Transit** (`frontend/lib/encryption.ts`)
   - For emergency access: encrypt `patient_id + access_key` before sending (client-side optional layer)
   - Or: implement TLS/HTTPS enforced (production)

---

### PHASE 5: Database & Deployment Hardening (Days 5-6)

1. **Replace CSV with PostgreSQL**
   - Create schema:
     - `users` (address PK, role, created_at, updated_at, is_active)
     - `health_data` (id, address FK, heart_rate, temperature, spo2, timestamp, created_at)
     - `audit_logs` (id, actor_address FK, action, resource_id, result, timestamp)
     - `access_tokens_blacklist` (jti PK, expiration_time)
   - Add migrations (Alembic)

2. **Database Service** (`backend/app/services/database_service.py`)
   - CRUD operations for all entities
   - Connection pooling (SQLAlchemy with pool_pre_ping)
   - Encryption at rest (use database native or app-level)

3. **Environment Configuration** (`config/settings.py` + `.env`)
   - Separate dev/staging/prod configs
   - Load from `.env` file (never commit)
   - Required secrets: JWT_PRIVATE_KEY, DB_PASSWORD, BLOCKCHAIN_PRIVATE_KEY
   - Validation: raise error if required env vars missing

4. **Rate Limiting** (`backend/app/middleware/rate_limit.py`)
   - Use `slowapi` library
   - Limit: 100 requests/minute per IP for public endpoints
   - Limit: 1000 requests/minute per user for authenticated endpoints
   - Limit: 5 login attempts/minute per IP

5. **CORS Hardening** (`backend/app/main.py`)
   - Allow only frontend domain (e.g., `https://securemedi.example.com`)
   - Allow only specific methods: GET, POST, PUT, DELETE (not OPTIONS wildcard)
   - Allow only necessary headers: Content-Type, Authorization

6. **Secrets Management**
   - Create `.env.example` with required variables
   - Document: "Never commit `.env`"
   - For production: use environment variables from deployment platform (Docker, Kubernetes)

7. **Docker & Deployment** (`Dockerfile`, `docker-compose.yml`)
   - Backend Dockerfile: multi-stage build, non-root user
   - Frontend Dockerfile: Next.js production build
   - Docker-compose: PostgreSQL, Redis (for token blacklist), backend, frontend
   - Environment variables passed via docker-compose
   - Health checks for all services

---

### PHASE 6: Testing & Documentation (Days 6-7)

1. **Backend Integration Tests** (`tests/test_auth.py`, `tests/test_rbac.py`)
   - Test JWT generation/refresh
   - Test token expiration & refresh
   - Test RBAC middleware on protected routes
   - Test audit logging

2. **Frontend Tests** (`frontend/tests/auth.test.ts`)
   - Test token storage encryption/decryption
   - Test role-based route protection
   - Test API interceptor refresh logic

3. **Security Tests**
   - Test SQL injection prevention (ORM parametrized queries)
   - Test XSS prevention (Pydantic validation, React auto-escaping)
   - Test CSRF (token-based, same-site cookies)
   - Test access control (unauthorized user requests)

4. **API Documentation** (`docs/API.md`)
   - Endpoint list with auth requirements
   - Request/response examples
   - Error codes & meanings

5. **Security Documentation** (`docs/SECURITY.md`)
   - Auth flow diagram (JWT generation → refresh → logout)
   - RBAC matrix (roles vs. actions)
   - Incident response guide
   - Deployment checklist

6. **Deployment Guide** (`docs/DEPLOYMENT.md`)
   - Step-by-step production deployment
   - SSL/TLS setup
   - Environment variable configuration
   - Database migration steps

---

## Relevant Files

**To Create:**
- `backend/app/services/jwt_service.py` — JWT generation/validation
- `backend/app/middleware/auth.py` — Token extraction & validation
- `backend/app/middleware/rbac.py` — Role-based access control decorators
- `backend/app/middleware/audit.py` — Request/response logging
- `backend/app/services/audit_service.py` — Audit log storage/retrieval
- `backend/app/services/database_service.py` — PostgreSQL CRUD
- `backend/app/middleware/rate_limit.py` — Rate limiting
- `backend/app/api/admin_routes.py` — Admin endpoints
- `backend/app/api/audit_routes.py` — Audit endpoints
- `backend/config/database.py` — Database connection setup
- `frontend/middleware/authMiddleware.ts` — Token refresh interceptor
- `frontend/middleware/protectedRoutes.ts` — Private route wrapper
- `frontend/lib/encryption.ts` — Client-side encryption
- `frontend/lib/validators.ts` — Input validation
- `tests/test_auth.py` — Auth integration tests
- `tests/test_rbac.py` — RBAC tests
- `frontend/tests/auth.test.ts` — Frontend auth tests
- `docs/API.md` — API documentation
- `docs/SECURITY.md` — Security guide
- `docs/DEPLOYMENT.md` — Deployment guide
- `.env.example` — Environment template

**To Modify:**
- `backend/app/main.py` — Add middleware, CORS hardening
- `backend/app/api/auth_routes.py` — JWT integration
- `backend/app/services/auth_service.py` — Fix patient auth, add access control
- `config/settings.py` — Add database & security configs
- `frontend/lib/api.ts` — Token refresh logic
- `frontend/lib/auth.ts` — Encrypted storage
- `frontend/next.config.js` — Security headers
- `docker-compose.yml` — Add PostgreSQL & Redis
- `backend/requirements.txt` — Add jwt, database, rate-limit libraries
- `.gitignore` — Already updated

---

## Verification

**Phase 1 Completion:**
- JWT tokens signed & verified ✓
- Refresh endpoint working ✓
- Logout invalidates tokens ✓
- Patient auth calling blockchain ✓

**Phase 2 Completion:**
- All protected routes enforce authentication ✓
- RBAC decorators protect sensitive routes ✓
- Unauthorized requests return 403 ✓
- Admin endpoints secured ✓

**Phase 3 Completion:**
- All sensitive operations logged ✓
- Audit logs queryable by user & admin ✓
- Critical logs on blockchain ✓

**Phase 4 Completion:**
- Frontend auto-refreshes expiring tokens ✓
- Token storage encrypted ✓
- Protected routes prevent unauthorized access ✓
- Input validation prevents malformed requests ✓

**Phase 5 Completion:**
- PostgreSQL schema created & migrated ✓
- All CSV data migrated to DB ✓
- Rate limiting active ✓
- Docker containers run without warnings ✓
- Environment variables properly configured ✓

**Phase 6 Completion:**
- 90%+ test coverage for auth/rbac ✓
- All endpoints documented ✓
- Security guide complete ✓
- Deployment guide tested ✓

---

## Key Architecture Changes

### Current Flow:
```
Client → (unprotected routes) → Services → (CSV/Blockchain)
```

### New Flow:
```
Client (encrypted token + auth interceptor)
  ↓ (Authorization header)
Backend (auth middleware validates JWT)
  ↓ (token.state injected)
Routes (RBAC middleware checks role)
  ↓ (permission enforced)
Services (audit logging on entry)
  ↓ (audit logging on exit)
Database (encrypted storage)
```

---

## Critical Decisions

1. **JWT over sessions?** YES — Stateless, easier to scale, works with frontend SPA
2. **PostgreSQL over CSV?** YES — Healthcare data requires relational integrity & ACID compliance
3. **httpOnly cookies or Authorization header?** Authorization header (current setup works, but httpOnly would be more secure for production). Plan accounts for both.
4. **Encrypt tokens client-side?** YES — Defense in depth against XSS
5. **Block all requests without token?** YES — Fail-secure approach
6. **Blockchain for audit logs or database?** BOTH — Critical logs immutable on blockchain, operational logs in DB

---

## Timeline & Dependencies

- Phase 1 & 2 must complete before Phase 3 (need protected routes first)
- Phase 3 & 4 are independent (can parallelize)
- Phase 5 depends on Phases 1-3 (need auth & audit ready)
- Phase 6 depends on all others (testing & docs come last)

**Total Effort:** ~40-50 hours for a single developer. With 2 people, ~25-30 hours.
