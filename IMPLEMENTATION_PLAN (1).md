# Implementation Plan — AI Presentation Reviewer (MVP)

## Goal

A basic web app with no login, sessions, or accounts:

1. User uploads a slide deck (PowerPoint or PDF).
2. App extracts the text/images from the slides.
3. Claude evaluates the deck against a fixed rubric.
4. App displays a rubric score + written feedback.

That's it. Everything else (video, multi-LLM comparison, accounts, analytics) is explicitly out of scope for this milestone — see the original Project Planner's "Stretch Goals" for later.

---

## Architecture (MVP)

Static frontend on **GitHub Pages** + a small **serverless function** (Cloudflare Workers or Vercel Functions) that holds the Claude API key and does the actual work. No server to stand up, deploy, or maintain — this keeps the team focused on the core upload → extract → evaluate → feedback loop instead of infra.

```
GitHub Pages (static site: HTML/JS, no build step required)
      │  file upload (multipart/form-data)
      ▼
Serverless function  (Cloudflare Worker or Vercel Function)
   └─ single endpoint, e.g. POST /api/evaluate
        1. receive uploaded file
        2. extract slide text (pptx/pdf)
        3. call Claude API with rubric prompt
        4. parse JSON response
        5. return { scores, feedback } to the browser
      │
      ▼
Claude API (LLM judge) — key lives only in the function's environment vars, never in the frontend
      │
      ▼
Browser renders score + feedback
```

Why this shape:
- **GitHub Pages** can only serve static files — it cannot call Claude directly, because that would expose the API key in client-side JS. The serverless function is what keeps the key secure.
- No database, no sessions, no server to manage — the function runs per-request and returns a result. Nothing persists between requests.
- One function endpoint is enough for MVP; it can internally call a shared "extract" step and an "evaluate" step rather than exposing them as separate endpoints.

**Suggested stack:**
- Frontend: plain HTML/CSS/JS (or a lightweight framework if the team prefers), deployed via GitHub Pages
- Backend: **Cloudflare Workers** (recommended — generous free tier, fast cold starts, simple `wrangler` CLI) or **Vercel Functions** as an alternative
- File parsing: JS/TS libraries that run in the Workers/Vercel runtime — e.g. a pptx parser compatible with Workers (e.g. `unzipper`/`jszip` + XML parsing, since `.pptx` is a zip of XML) and a PDF text extractor (e.g. `pdf-parse` on Vercel Node runtime, or an unpdf/PDF.js-based approach if targeting Workers)
- LLM: Claude API (`claude-sonnet-4-6` or current default model), called from the function with the key stored as a secret/environment variable

Note: Cloudflare Workers and Vercel Functions have different runtime constraints (Workers = V8 isolate, no Node APIs by default; Vercel = full Node.js runtime available). If PDF/PPTX parsing libraries turn out to need Node APIs, **Vercel Functions** will be the easier path — worth confirming this with a quick spike in Phase 0 before committing.

---

## Rubric (fixed for MVP)

| Category | Points |
|---|---|
| Organization | 10 |
| Clarity | 10 |
| Content Quality | 10 |
| Professionalism | 10 |
| Overall Impression | 10 |

Claude should return strict JSON so the frontend can render it reliably, e.g.:

```json
{
  "scores": {
    "organization": 8,
    "clarity": 9,
    "content_quality": 7,
    "professionalism": 10,
    "overall_impression": 8
  },
  "feedback": [
    "Strong slide organization.",
    "Reduce text on slides 4-6.",
    "Include more supporting evidence."
  ]
}
```

---

## Phased Breakdown (each phase = a batch of GitHub issues)

### Phase 0 — Project Setup
- [ ] Initialize repo structure (`/frontend` for the static site, `/functions` or `/api` for the serverless function, README)
- [ ] Add `.gitignore` (exclude `.env`, `node_modules`, wrangler/vercel local config)
- [ ] Add `.env.example` documenting required secrets (e.g. `ANTHROPIC_API_KEY`)
- [ ] Spike: confirm pptx/pdf parsing libraries work in the chosen runtime (Cloudflare Workers vs Vercel Functions) — pick whichever runtime doesn't fight the parsing libraries
- [ ] Set up the serverless function project (`wrangler init` or `vercel` scaffold) with a health check endpoint
- [ ] Set up GitHub Pages to serve the static frontend, confirm it loads and can hit the health check endpoint

### Phase 1 — File Upload
- [ ] Build the function's file-receiving logic (`POST /api/evaluate` accepts multipart upload of `.pptx`/`.pdf`)
- [ ] Validate file type and size in the function before processing
- [ ] Build simple upload form on the static frontend (file picker + submit button)
- [ ] Wire the frontend form to POST to the deployed function URL
- [ ] Show upload success/failure state to the user

### Phase 2 — Content Extraction
- [ ] Implement PPTX text extraction (slide titles, body text, speaker notes if present) inside the function
- [ ] Implement PDF text extraction (per-page text) inside the function
- [ ] Normalize both into a common internal format: `[{slide_number, text}]`
- [ ] Handle edge cases: empty slides, image-only slides, corrupted files
- [ ] Unit tests for extraction logic (run locally, outside the deployed function, on a few sample decks)

### Phase 3 — LLM Evaluation
- [ ] Write the rubric prompt template (system prompt instructing Claude to return only JSON)
- [ ] Implement Claude API call from the function, with the API key read from environment/secrets (never sent to the frontend)
- [ ] Parse and validate the JSON response (handle malformed output gracefully — retry once if parsing fails)
- [ ] Add basic error handling (API timeout, rate limit, invalid key) with a clear error returned to the frontend

### Phase 4 — Display Results
- [ ] Confirm the function returns `{ scores, feedback }` end-to-end from a single upload call
- [ ] Render rubric scores on the frontend (simple table or list — no need for progress bars/color-coding yet, that's a stretch goal)
- [ ] Render written feedback as a bullet list
- [ ] Handle and display error states (bad file, extraction failure, LLM failure)

### Phase 5 — End-to-End Polish
- [ ] Manual test with a handful of real sample decks (mix of good/bad presentations) against the deployed function
- [ ] Tighten the rubric prompt based on test results (consistency of scoring)
- [ ] Basic loading state while processing (uploads/evaluation can take a few seconds)
- [ ] README with setup instructions (env vars/secrets, how to run the function locally, how to deploy to GitHub Pages + Cloudflare/Vercel, how to test)

---

## Explicitly Out of Scope for MVP

These are documented in the original planner as stretch goals — do not build them yet:

- Video upload / speech-to-text / delivery evaluation
- Color-coded UI, progress bars, downloadable PDF reports
- Comparing multiple LLMs (GPT, Gemini, local models)
- User accounts, login, saved history, analytics dashboard
- Google Slides / Canva integration and permission-checking
- Slack notifications, tracking spreadsheets, auto-posting to Padlet/Drive

## GitHub Issues Checklist

Flat, numbered version of the phase breakdown above — one issue per line.

**Phase 0 — Project Setup**
1. Initialize repo structure (`/frontend`, `/functions` or `/api`, README)
2. Add `.gitignore` (exclude `.env`, `node_modules`, wrangler/vercel local config)
3. Add `.env.example` documenting required secrets (e.g. `ANTHROPIC_API_KEY`)
4. Spike: confirm pptx/pdf parsing libraries work in the chosen runtime (Cloudflare Workers vs Vercel Functions)
5. Set up the serverless function project with a health check endpoint
6. Set up GitHub Pages to serve the static frontend; confirm it can hit the health check endpoint

**Phase 1 — File Upload**
7. Build the function's file-receiving logic (`POST /api/evaluate` accepts `.pptx`/`.pdf`)
8. Validate file type and size in the function before processing
9. Build simple upload form on the static frontend (file picker + submit button)
10. Wire the frontend form to POST to the deployed function URL
11. Show upload success/failure state to the user

**Phase 2 — Content Extraction**
12. Implement PPTX text extraction (titles, body text, speaker notes) inside the function
13. Implement PDF text extraction (per-page text) inside the function
14. Normalize both into a common internal format: `[{slide_number, text}]`
15. Handle edge cases: empty slides, image-only slides, corrupted files
16. Unit tests for extraction logic on a few sample decks

**Phase 3 — LLM Evaluation**
17. Write the rubric prompt template (system prompt instructing Claude to return only JSON)
18. Implement Claude API call from the function, with the API key read from environment/secrets
19. Parse and validate the JSON response (retry once if parsing fails)
20. Add basic error handling (API timeout, rate limit, invalid key) with a clear error to the frontend

**Phase 4 — Display Results**
21. Confirm the function returns `{ scores, feedback }` end-to-end from a single upload call
22. Render rubric scores on the frontend (simple table or list)
23. Render written feedback as a bullet list
24. Handle and display error states (bad file, extraction failure, LLM failure)

**Phase 5 — End-to-End Polish**
25. Manual test with a handful of real sample decks against the deployed function
26. Tighten the rubric prompt based on test results (consistency of scoring)
27. Add a basic loading state while processing

Plus one more from setup:
28. Write README with setup instructions (env vars/secrets, running the function locally, deploying to GitHub Pages + Cloudflare/Vercel, how to test)

## Next Step

Once this plan is agreed on, create the 28 issues above in GitHub (one per line). Phases 0–2 can likely be worked on in parallel by different team members since they don't depend on each other; Phase 3 depends on Phase 2's output format being settled first.
