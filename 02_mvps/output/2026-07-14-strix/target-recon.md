# Target Recon: axross-recipe.com

## Basic Info

| Item | Value |
|---|---|
| URL | https://axross-recipe.com |
| Title | Axross Recipe |
| Description | AI/Data Science learning platform by SoftBank |
| Language | Japanese (ja) |
| Protocol | HTTPS only |

## Tech Stack

| Layer | Technology | Evidence |
|---|---|---|
| Frontend Framework | Next.js (Turbopack) | `_next/static/chunks/turbopack-*.js` |
| Frontend Hosting | Vercel-like (Next.js SSR) | Response headers, `__next/` paths |
| API Backend | Rails (Ruby on Rails) | `x-runtime`, `x-request-id`, `x-frame-options: SAMEORIGIN`, `etag` format |
| API Domain | api.axross-recipe.com | All JSON API calls go to separate subdomain |
| Auth | NextAuth.js | `/api/auth/session`, `__Host-next-auth.csrf-token` cookie |
| Analytics | Google Analytics (UA + GA4) | `UA-163661994-1`, `G-SBYLLX1T6E` |
| Image CDN | api.axross-recipe.com/attachments | User avatar and recipe eyecatch images |
| i18n | i18next | `/locales/ja/translation.json`, `i18nextLng=ja` localStorage |
| Fonts | Google Fonts + Font Awesome + Material Icons | CDN imports |

## API Endpoints Discovered

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `api.axross-recipe.com/recipes` | GET | No | List recipes (supports `?ids=` comma-separated) |
| `api.axross-recipe.com/recipes/:id` | GET | No | Single recipe detail |
| `api.axross-recipe.com/users` | GET | No | User info (supports `?recipe_ids=`) |
| `api.axross-recipe.com/users/me/equivalent_finished_recipe_ids` | GET | **Required** (403) | User-specific data |
| `api.axross-recipe.com/configs` | GET | No | App configuration (public) |
| `api.axross-recipe.com/activity_logs/page_view` | POST | No | Page view tracking |
| `axross-recipe.com/api/auth/session` | GET | No | NextAuth session (returns `{}` unauthenticated) |

## Routes & Pages

| Route | Description |
|---|---|
| `/` | Landing page |
| `/recipes` | Recipe listing / search |
| `/recipes/:id` | Single recipe detail |
| `/signin` | Login page |
| `/signup` | Registration page |
| `/users/:id` | User profile |
| `/news_items` | News/announcements |
| `/terms` | Terms of service |
| `/privacy` | Site privacy policy |
| `/helps/top` | Help center |
| `/helps/development_environment` | Dev environment setup guide |
| `/tsh` | Legal (特定商取引法) |

## Authentication

- **Framework**: NextAuth.js v4+
- **CSRF Token Cookie**: `__Host-next-auth.csrf-token` (HttpOnly, Secure, SameSite=Lax)
- **Callback Cookie**: `__Secure-next-auth.callback-url` (HttpOnly, Secure, SameSite=Lax)
- **Session Cookie**: None when unauthenticated (session is `{}`)

## Security Headers (api.axross-recipe.com)

| Header | Value |
|---|---|
| `x-frame-options` | SAMEORIGIN |
| `x-content-type-options` | nosniff |
| `x-xss-protection` | 0 (disabled) |
| `x-download-options` | noopen |
| `x-permitted-cross-domain-policies` | none |
| `referrer-policy` | strict-origin-when-cross-origin |
| `access-control-allow-origin` | https://axross-recipe.com |
| `access-control-allow-methods` | GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD |

## Security Headers (axross-recipe.com)

| Header | Value |
|---|---|
| `content-security-policy` | `frame-ancestors 'none'` |
| `x-frame-options` | DENY |

## Attack Surface Summary

| Area | Observations |
|---|---|
| Registration/Signup | `/signup` - free registration, potential for mass account creation |
| Login | `/signin` - NextAuth, potential for brute force / credential stuffing |
| Recipe CRUD | User-created content with Markdown editor - potential XSS via Markdown |
| Comments | Commenting system - potential XSS, CSRF |
| File Upload | Attachment system (`api.axross-recipe.com/attachments`) - potential file upload vulns |
| User Search | `/recipes?ids=` with comma-separated params - potential IDOR |
| API | Separate subdomain `api.axross-recipe.com` - CORS policies restrict to main domain |
| Organization | Organization-based visibility (`org_visibility: same_organization`) - potential for cross-org access |
