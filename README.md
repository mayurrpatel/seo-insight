# SEO Insight — Website SEO Audit & Fix Prioritizer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20%2B%20Vitest-success.svg)](https://docs.pytest.org)

**SEO Insight** is a full-stack web application built for an internship assessment that crawls authorized public websites, detects technical and on-page SEO issues, categorizes them by severity, and generates an evidence-backed, prioritized list of fixes with actionable remediation guidance.

---

## 1. Project Overview & Architecture

Unlike superficial surface auditors, **SEO Insight** implements real, rule-based crawler and parser engines with transparent scoring models and enterprise security guardrails.

```
┌─────────────────────────────────────────────────────────────┐
│                      React 18 + Vite                        │
│  - Modern SaaS Dashboard (White/Slate/Navy)                 │
│  - Health Score Dial & Severity Distribution Charts         │
│  - Searchable, Filterable, Sortable Prioritized Table       │
│  - Issue Detail Drawer (Evidence, Impact, Suggested Fixes)  │
│  - Live Crawl Progress & CSV / HTML Report Downloads        │
└──────────────────────────────▲──────────────────────────────┘
                               │ REST / JSON (FastAPI)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Python Backend                   │
│                                                             │
│  ┌──────────────────────┐       ┌────────────────────────┐  │
│  │   SSRF Protection    │       │   Robots.txt Parser    │  │
│  │ - Rejects Localhost  │       │ - Obeys disallow rules │  │
│  │ - Blocks 10.x, 192.x │       │ - Detects XML Sitemaps │  │
│  │ - Blocks Cloud Meta  │       │ - Domain-scoped crawl  │  │
│  └──────────┬───────────┘       └───────────┬────────────┘  │
│             │                               │               │
│  ┌──────────▼───────────────────────────────▼────────────┐  │
│  │               Async Domain Crawler                    │  │
│  │  - Httpx async engine with redirect chain tracking    │  │
│  │  - BeautifulSoup4 DOM parsing & link extraction       │  │
│  │  - Rate limiting & request timeout protections        │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │        SEO Rules & Prioritization Engine              │  │
│  │  - 15+ On-page & cross-page technical SEO rules       │  │
│  │  - Critical, High, Medium, Low severity ranking       │  │
│  │  - Normalized Health Score Calculation (0-100)        │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │         RFC 4180 CSV & Standalone HTML Reports        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Key Features

### A. Responsible Web Crawling & SSRF Safeguards
- **Anti-SSRF Protection:** Validates target domain and every redirect destination. Blocks `localhost`, `127.0.0.1`, private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local/cloud metadata (`169.254.169.254`), and non-HTTP protocols.
- **Robots.txt Compliance:** Fetches and parses `/robots.txt` before crawling; halts if bot user-agent is disallowed.
- **Domain-Bounded Crawling:** Confines crawling to the input hostname.
- **Controlled Page Limits & Timeouts:** Configurable scan depth (3–25 pages, default 12) with per-request 8s timeouts and rate limits to prevent overloading target servers.

### B. Rule-Based SEO Detection
Evaluates confirmed findings across 5 primary SEO categories:
1. **Title Tags:** Detects missing titles, multiple titles, too short (< 20 chars), and SERP-truncated titles (> 65 chars).
2. **Meta Descriptions:** Flags missing descriptions, too short (< 50 chars), and truncated descriptions (> 165 chars).
3. **Headings Hierarchy:** Detects missing `<h1>`, multiple `<h1>` tags, and skipped heading levels (e.g. `H1 -> H3`).
4. **Image Accessibility:** Identifies all `<img>` elements missing `alt` attributes, providing exact source URLs.
5. **Canonicalization:** Flags missing canonical tags, conflicting/multiple canonicals, and relative canonical URLs.
6. **Robots Directives & Indexability:** Checks for `noindex` and `nofollow` in `<meta>` and `X-Robots-Tag` headers.
7. **Security & Protocol:** Detects insecure plain HTTP and mixed content assets (HTTP images/scripts on HTTPS pages).
8. **Navigation & Links:** Detects 4xx/5xx HTTP errors, broken internal links, redirect chains (> 2 hops), and broken external links.
9. **Cross-Page Duplicates:** Evaluates identical `<title>` tags and `<meta description>` content across pages.
10. **Sitemap & Robots Presence:** Verifies discovery of `robots.txt` and `sitemap.xml`.

### C. Health Score & Prioritization Model
- **Health Score (0–100):** Calculated from actual scan findings using a normalized weighted penalty:
  $$\text{Normalized Penalty} = \frac{\sum (\text{Issue Count} \times \text{Weight})}{\text{Pages Scanned}^{0.65}} \times 1.8$$
  $$\text{Health Score} = \max(0, \min(100, 100 - \text{Normalized Penalty}))$$
  - **Critical Issue:** $-25\text{ pts}$ (e.g. Server 500 error, missing title tag, multiple canonicals)
  - **High Priority:** $-15\text{ pts}$ (e.g. Missing H1, missing meta description, broken internal link, mixed content)
  - **Medium Priority:** $-8\text{ pts}$ (e.g. Missing image alts, relative canonical, redirect chain)
  - **Low Priority:** $-3\text{ pts}$ (e.g. Title slightly too long, meta description too short)
- **Priority Scores (1–100):** Every individual finding has a calculated priority score allowing instant sorting.
- **Important Disclaimer:** All findings reflect technical crawl hygiene and webmaster standards, not guaranteed Google ranking improvements.

### D. Exportable Audit Reports & Database History
- **SQLite Database Persistence:** Every completed audit is automatically saved into a local SQLite database (`backend/seo_insight.db`). Past audit reports persist across server restarts, and can be viewed, searched, exported, or deleted at any time.
- **Interactive Saved Reports Drawer:** Access all previously audited websites with their domain, score badge, date, issue breakdown, and 1-click report loader.
- **RFC 4180 CSV Export:** Direct spreadsheet download with issue ID, category, severity, priority score, affected URL, occurrences, evidence, and suggested fix.
- **Standalone HTML Report:** Self-contained, printable executive report complete with health score dials, executive metrics, issue cards, and responsive print-to-PDF styles (`@media print`).
- **One-Click Sample Report:** Pre-packaged illustrative audit data (`https://acme-analytics-demo.io`) to test the application immediately without live network dependency.

---

## 3. Technology Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic, HTTPX, BeautifulSoup4, Jinja2.
- **Frontend:** React 18, Vite 6, Lucide React (Clean SaaS design system).
- **Testing:** Pytest (Backend API, rules, SSRF, crawler), Vitest + React Testing Library (Frontend UI).

---

## 4. Getting Started

### Prerequisites
- **Python 3.10+** (tested on 3.12)
- **Node.js 18+** and **npm**

### Backend Setup & Run

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   python main.py
   ```
   *The backend will be available at `http://127.0.0.1:8000` (Swagger docs at `http://127.0.0.1:8000/docs`).*

### Frontend Setup & Run

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will be available at `http://localhost:5173`.*

---

## 5. Running Automated Tests

### Backend Tests (Pytest)
Run the 29 backend unit and integration tests:
```bash
cd backend
python -m pytest
```
*Tests cover SSRF protection, URL validation, all SEO rules (titles, meta, headings, canonicals, alts, mixed content), scoring calculation, SQLite database persistence, crawler filtering, and API endpoints.*

### Frontend Tests (Vitest)
Run the 9 React unit and component tests:
```bash
cd frontend
npm test
```
*Tests cover health score card rendering, issue table searching and filtering, audit history modal, and inspection modal drawer interactions.*

### Frontend Production Build
Verify the production build assets:
```bash
cd frontend
npm run build
```

---

## 6. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check and server status. |
| `GET` | `/api/audits/history` | Retrieves all previously audited reports from SQLite database. |
| `POST` | `/api/audit` | Starts a new asynchronous website audit session. |
| `GET` | `/api/audit/status/{id}` | Polls crawl progress, pages scanned, and failures. |
| `GET` | `/api/audit/{id}` | Retrieves completed audit results with findings & scores (from memory or SQLite). |
| `DELETE` | `/api/audit/{id}` | Deletes an audit from the SQLite database. |
| `GET` | `/api/sample-audit` | Returns instant illustrative sample audit data. |
| `GET` | `/api/audit/{id}/csv` | Downloads findings as an RFC 4180 CSV file. |
| `GET` | `/api/audit/{id}/report`| Downloads a self-contained, printable HTML report. |

#### Sample Start Audit Payload:
```json
POST /api/audit
{
  "url": "https://example.com",
  "max_pages": 12
}
```

---

## 7. Deployment Instructions

### Backend (Render, Railway, or Fly.io)
1. Point your service to the `backend/` directory.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment variables:
   - `PORT`: (provided by host, default `8000`)
   - `CORS_ORIGINS`: comma-separated list of allowed frontend domains.

### Frontend (Vercel, Netlify, or Cloudflare Pages)
1. Point your deployment to the `frontend/` directory.
2. Build command: `npm run build`
3. Output directory: `dist`
4. Environment variables:
   - `VITE_API_URL`: URL of your deployed backend (e.g. `https://your-api.onrender.com`).

---

## 8. Responsible Usage & Limitations

1. **Authorization Notice:** Users must only audit websites they own or have explicit written permission to test.
2. **Auditing Priorities vs. Google Ranking:** Finding priorities indicate technical best-practice hygiene and search crawler access. They do not claim or guarantee organic search ranking improvements.
3. **JavaScript-Rendered Content (SPAs):** Crawling uses fast, server-side HTTP parsing with BeautifulSoup. Client-side JavaScript-only applications that require headless browser execution (such as full Puppeteer/Playwright rendering) should be pre-rendered or audited using server-rendered HTML.
4. **Third-Party APIs:** SEO Insight intentionally uses zero paid third-party APIs (no Google Search Console or Ahrefs API keys required) to ensure 100% beginner-maintainable local operation.

---

## 9. License
MIT License. Built for educational and internship assessment purposes.
