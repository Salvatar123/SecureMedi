# Phase 4: Frontend Security Hardening - Implementation Guide

## Overview

Phase 4 implements comprehensive client-side security measures to protect user credentials, prevent common web attacks, and ensure secure communication with the backend API. This phase builds on the JWT authentication infrastructure from Phase 1-3.

## Key Security Features

### 1. Token Encryption (`frontend/lib/crypto.ts`)

**Purpose:** Encrypt tokens in memory and storage to prevent token theft from browser memory or storage compromises.

**Implementation:**
- **Algorithm:** AES-GCM (Advanced Encryption Standard with Galois/Counter Mode)
- **Key Size:** 256-bit keys
- **Session-based:** Encryption keys generated per session, never persisted
- **Functions:**
  - `generateEncryptionKey()` - Generate new 256-bit AES-GCM key
  - `encryptToken(token, key)` - Encrypt token with IV
  - `decryptToken(encryptedToken, key)` - Decrypt token
  - `deriveKeyFromPassword(password, salt)` - PBKDF2 key derivation
  - `isCryptoAvailable()` - Check browser crypto support

**Security Benefits:**
- Protects against token theft via XSS (encrypted tokens are useless without key)
- Prevents localStorage/sessionStorage exposure
- PBKDF2 ensures resistant to brute-force password attacks (100,000 iterations)

### 2. Secure Token Storage (`frontend/lib/secureStorage.ts`)

**Purpose:** Manage encrypted tokens in sessionStorage with secure access patterns.

**Storage Strategy:**
- **Access Token:** Encrypted, sessionStorage (15-min lifetime)
- **Refresh Token:** Encrypted, sessionStorage (7-day lifetime)  
- **Encryption Key:** In-memory only (never persisted)

**Key Functions:**
- `storeAccessToken(token, key)` - Encrypt and store access token
- `getAccessToken(key)` - Retrieve and decrypt access token
- `storeRefreshToken(token, key)` - Encrypt and store refresh token
- `getRefreshToken(key)` - Retrieve and decrypt refresh token
- `clearAllTokens()` - Secure logout (wipe all credentials)
- `hasAccessToken()` - Check token existence without decryption

**Security Benefits:**
- Tokens cleared on browser close (sessionStorage)
- Encryption key never written to disk
- Corrupted tokens cannot be used (clearEncryptionKey on error)
- Race condition protection for concurrent token operations

### 3. Input Sanitization & Validation (`frontend/lib/sanitization.ts`)

**Purpose:** Prevent injection attacks (XSS, SQL injection) through user input validation and sanitization.

**Core Functions:**
- **XSS Prevention:**
  - `sanitizeInput(input)` - Remove dangerous HTML/JS
  - `escapeHtml(text)` - Escape HTML special characters
  - `sanitizeHtml(html)` - Remove scripts and event handlers from HTML

- **Format Validation:**
  - `isValidEmail(email)` - Email RFC 5322 validation
  - `isValidEthereumAddress(address)` - Ethereum address (0x prefixed hex)
  - `isValidJWT(token)` - JWT format (3 dot-separated parts)
  - `isValidUrl(url)` - URL scheme validation (http/https only)

- **Security Validation:**
  - `isStrongPassword(password)` - Require 8+ chars, upper, lower, number, special
  - `getPasswordStrengthFeedback(password)` - User guidance
  - `getSafeRedirectUrl(url)` - Prevent open redirect attacks
  - `limitStringLength(input, maxLength)` - DoS prevention

**Example Usage:**
```typescript
const address = sanitizeInput(userInput.trim());
if (!isValidAddress(address)) {
  throw new Error("Invalid address");
}
```

### 4. Secure API Client (`frontend/lib/secureApi.ts`)

**Purpose:** Provide CSRF-protected, token-refreshing API client with automatic security headers.

**Features:**
- **CSRF Protection:** `X-Requested-With: XMLHttpRequest` header
- **Auto Token Refresh:** 401 responses trigger token refresh flow
- **Automatic Retry:** Failed requests retried with new token
- **Secure Headers:** No credentials sent, cache control, XSS protection
- **Error Handling:** Clear error messages, sensitive data redaction

**Key Functions:**
- `createSecureApiClient()` - Create axios client with interceptors
- `getApiClient()` - Get singleton API client instance
- `loginWithEncryption(loginData, encKey)` - Secure login with token storage
- `logout()` - Clear tokens and reset API client
- `requestAccessKey(patientId)` - Public endpoint (no auth needed)
- `verifyToken(token)` - Verify token validity with server

**Interceptors:**

**Request Interceptor:**
- Extracts and decrypts access token
- Adds to Authorization header
- Sets security headers (no CORS credentials)

**Response Interceptor:**
- Detects 401 Unauthorized responses
- Automatically requests new access token using refresh_token
- Retries original request with new token
- Handles 403 Forbidden and other errors
- Clears tokens and redirects to login on fatal auth failure

### 5. Protected Routes (`frontend/lib/protectedRoute.tsx`)

**Purpose:** Enforce authentication and authorization on frontend routes.

**Components:**
- **`withProtectedRoute(Component, options)`** - HOC for class/functional components
- **`<ProtectedRoute>`** - Functional component for route wrapping

**Features:**
- Redirect to login if not authenticated
- Redirect to error page if insufficient role
- Display loading spinner during auth check
- Support for role-based access control (DOCTOR, PATIENT, ADMIN)
- Optional fallback URL (default: /login)

**Usage:**
```typescript
// HOC approach
export default withProtectedRoute(Dashboard, { requiredRole: 'DOCTOR' });

// Component approach
<ProtectedRoute requiredRole="PATIENT">
  <PatientDashboard />
</ProtectedRoute>
```

### 6. Authentication State Management (`frontend/stores/authStore.ts`)

**Purpose:** Centralized auth state with encryption key lifecycle management.

**Store Actions:**
- `initializeEncryption()` - Generate session encryption key
- `setUser(user, role)` - Update user info after login
- `setAuthenticated(isAuth)` - Set auth status
- `logout()` - Clear all auth data and tokens
- `checkTokenValidity()` - Verify token presence and encryption key
- `clearError()` - Reset error state

**State:**
- `user` - User address and name
- `userRole` - DOCTOR, PATIENT, or ADMIN
- `isAuthenticated` - Boolean flag
- `encryptionKey` - Active CryptoKey (in memory only)
- `encryptionAvailable` - Browser crypto API support
- `isLoading` - Operation in progress
- `error` - Error message if any

**Initialization:**
```typescript
// In _app.tsx or root component
export function useInitializeAuth() {
  const { encryptionKey, initializeEncryption } = useAuthStore();
  
  useEffect(() => {
    if (!encryptionKey) {
      initializeEncryption();
    }
  }, []);
}
```

### 7. Security Headers (`frontend/lib/securityConfig.ts`)

**HTTP Security Headers:**
```
X-Content-Type-Options: nosniff             # Prevent MIME sniffing
X-Frame-Options: DENY                       # Prevent clickjacking
X-XSS-Protection: 1; mode=block            # Enable XSS filter
Referrer-Policy: strict-origin-when-cross-origin  # Limit referrer
Permissions-Policy: geolocation=()...       # Disable unnecessary APIs
CSP: default-src 'self'...                 # Content Security Policy
```

**Configuration in `next.config.js`:**
- Applied to all routes via Next.js headers config
- Customizable per route if needed
- Production-ready default values

### 8. Updated Login Page (`frontend/pages/login.tsx`)

**Security Enhancements:**
- **Encryption Key Generation:** Creates session key on login
- **Input Sanitization:** Validates and sanitizes address field
- **Crypto Support Check:** Warns if browser doesn't support encryption
- **Error Display:** Clear error messages without leaking internals
- **Form Validation:** Required fields, format validation
- **Status Messages:** Real-time feedback (loading, errors)

**Login Flow:**
1. Generate encryption key
2. Sanitize user inputs
3. Validate address format
4. POST credentials to backend
5. Receive and store encrypted tokens
6. Update auth store
7. Redirect to dashboard or specified URL

## Implementation Checklist

- [x] Token encryption with AES-GCM
- [x] Secure encrypted storage (sessionStorage)
- [x] Input validation and XSS prevention
- [x] CSRF-protected API client
- [x] Automatic token refresh on 401
- [x] Protected route components
- [x] Encryption-aware auth store
- [x] Security headers in Next.js config
- [x] Updated login page with encryption
- [x] Crypto availability detection

## Configuration

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API server
```

### Browser Requirements

- **Required:** Modern browser with Web Crypto API support
  - Chrome 37+
  - Firefox 34+
  - Safari 11+
  - Edge 79+
- **Recommended:** Latest version for security patches

## Security Best Practices

### For Developers

1. **Never log tokens** - Even in development, avoid console.log of tokens
2. **Use HTTPS in production** - All communication must be encrypted
3. **Content Security Policy** - Keep CSP as strict as possible
4. **Regular updates** - Update dependencies for security patches
5. **Secrets management** - Never commit API keys or secrets

### For Users

1. **Keep browser updated** - Security patches are critical
2. **Use strong credentials** - Follow password strength requirements
3. **Don't share access keys** - Emergency access keys are sensitive
4. **Logout when done** - Closes session and clears tokens
5. **Use HTTPS** - Never login over unencrypted connections

## Migration from Phase 3

### For Existing Frontend Code

1. **Replace token storage:**
   ```typescript
   // Old
   localStorage.setItem('token', token);
   
   // New
   await storeAccessToken(token, encryptionKey);
   ```

2. **Update API calls:**
   ```typescript
   // Old
   const response = await apiClient.get('/api/health/latest');
   
   // New
   const client = getApiClient();
   const response = await client.get('/api/health/latest');
   ```

3. **Protect routes:**
   ```typescript
   // Old
   export default Dashboard;
   
   // New
   export default withProtectedRoute(Dashboard, { requiredRole: 'DOCTOR' });
   ```

4. **Update auth store imports:**
   ```typescript
   // Old
   import { useAuthStore } from '@/lib/auth';
   
   // New
   import { useAuthStore } from '@/stores/authStore';
   ```

## Testing Phase 4

### Manual Testing

1. **Login Flow:**
   - Test doctor login → verify encryption key generated
   - Test patient login → verify tokens encrypted
   - Test invalid credentials → verify error display

2. **Token Refresh:**
   - Make request → verify Authorization header
   - Wait 15 minutes → verify auto-refresh attempts
   - Use invalid token → verify 401 handling

3. **Protected Routes:**
   - Access without token → redirect to login
   - Access with wrong role → show 403 error
   - Access with correct role → load page

4. **Security:**
   - Disable JavaScript → verify no XSS from inputs
   - Test CSRF → verify X-Requested-With header
   - Try open redirect → verify safer redirect

### Security Testing

```bash
# Check for XSS vulnerabilities
curl -X POST http://localhost:3000/login \
  -d "address=<script>alert('xss')</script>"

# Verify CSP headers
curl -I http://localhost:3000 | grep Content-Security-Policy

# Check HTTPS redirects (production)
curl -I https://securemedi.example.com
```

## Troubleshooting

### "Encryption not available" Error

**Cause:** Browser doesn't support Web Crypto API  
**Solution:** Use a modern browser (Chrome 37+, Firefox 34+, Safari 11+)

### "Token decryption failed" Error

**Cause:** Encryption key or encrypted token is corrupted  
**Solution:** Clear localStorage/sessionStorage and login again

### Tokens not persisting across page reload

**Cause:** Using sessionStorage (cleared when tab closes)  
**Design:** Intentional for security - user must login per session  
**Alternative:** Use localStorage with encryption if needed (less secure)

### CORS errors on API calls

**Cause:** Missing security headers or wrong API URL  
**Solution:** Verify NEXT_PUBLIC_API_URL and CORS config in backend

## Next Steps: Phase 5

Phase 5 will focus on:
- Database migration (PostgreSQL)
- Production deployment hardening
- Certificate management
- Rate limiting and DDoS protection
- Logging and monitoring
- Backup and disaster recovery

---

**Last Updated:** April 8, 2026  
**Phase Status:** ✅ Complete - Frontend Security Hardening
