# Cybersecurity & Threat Mitigation Standard
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0) & OWASP ASVS Reference  
**Revision:** 1.0.0

---

## 1. Security Architecture & Principles

The application enforces **Secure by Design** and **Defense in Depth**:

1. **Parameter Sanitization & SQL Injection Protection**:
   - Every database query uses strict parameter binding via Python's standard `sqlite3` driver (`?` place-holders).
   - Dynamic raw SQL string concatenation is strictly prohibited across the codebase.

2. **Cross-Origin Resource Sharing (CORS)**:
   - Configurable CORS middleware in `server.py`.
   - Default configured to allow secure local origins and authorized cloud production domains.

3. **Client-Side Validation vs. Server-Side Authority**:
   - In accordance with MPADS Section 5, frontend validation is treated only as a UX enhancement.
   - All API endpoints validate incoming parameters (`day`, `market`, `min_prob`, `min_odds`, `value_only`) server-side via FastAPI and Pydantic types.

4. **Secret Management Policy**:
   - Zero hardcoded API keys, database credentials, or private tokens exist in the repository.
   - Environment-specific flags are handled via standard environment variables.
   - Client bundles contain no sensitive backend configuration or administrative secrets.

5. **External Ingestion Security**:
   - Playwright headless Chromium instances execute within isolated sandbox contexts (`--no-sandbox` only applied when operating within containerized environments).
   - Network responses are inspected for strict content-type verification (`application/json`) before parsing to prevent script injection.

---

## 2. Threat Modeling & Residual Risks

| Threat Vector | Mitigation Strategy | Risk Level |
| :--- | :--- | :---: |
| **SQL Injection** | Parameterized queries on all table insertions and queries. | **Low** |
| **XSS (Cross-Site Scripting)** | HTML sanitization and safe DOM insertion via innerText / escaping in UI. | **Low** |
| **Denial of Service (DoS)** | In-memory `SYNC_LOCK` prevents redundant resource exhaustion from overlapping scraping requests. | **Low** |
| **Data Poisoning** | Validation of ingested JSON schemas and fallback to persistent local cache if schema drifts. | **Low** |
| **Unencrypted HTTP (Android)** | Enforcement of HTTPS via Cloudflare Tunnel / SSL termination on cloud platforms to enable secure PWA installation. | **Low** |
