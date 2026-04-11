# SecureMedi Secret Rotation Checklist

Use this checklist after discovering committed key material.

## Immediate Containment

- [ ] Freeze deployments until key rotation is complete.
- [ ] Remove exposed key files from tracked sources.
- [ ] Confirm `.gitignore` covers all generated key paths.
- [ ] Invalidate all currently issued JWT access and refresh tokens.

## JWT Key Rotation

- [ ] Generate a fresh JWT private/public key pair.
- [ ] Set new values via environment variables: `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`.
- [ ] Do not commit generated keys to repository.
- [ ] Restart backend services so new keys are loaded.
- [ ] Verify old JWTs fail signature verification.
- [ ] Verify new login flow issues valid tokens.

## Blockchain Credential Rotation

- [ ] Replace any exposed blockchain private keys in runtime environments.
- [ ] Update `.env` on each environment with new `PRIVATE_KEY`.
- [ ] Confirm the replacement account has required on-chain permissions/balance.
- [ ] Re-run a smoke transaction to validate signing.

## Supabase/API Key Hygiene

- [ ] Rotate Supabase keys if any non-public/service keys were exposed.
- [ ] Ensure `.env` remains gitignored and never tracked.
- [ ] Verify no secrets exist in docs, examples, or test fixtures.

## Repository Hygiene

- [ ] Run a secret scan across tracked files before each release.
- [ ] Add pre-commit or CI secret scanning (for example: gitleaks).
- [ ] If secret was pushed to remote, rewrite git history and force-push.
- [ ] Notify collaborators to reclone or reset after history rewrite.

## Verification

- [ ] `git grep` returns no committed private key material.
- [ ] Backend starts and auto-generates local dev JWT keys when absent.
- [ ] Authentication and refresh workflows pass end-to-end tests.
- [ ] Document the incident date, scope, and recovery actions.
