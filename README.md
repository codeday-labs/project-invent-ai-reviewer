# project-invent-ai-reviewer

## Overview
A simple demo app with:
- a frontend upload UI
- a mock backend endpoint for evaluation results
- a Cloudflare Workers-ready API structure for future LLM integration

## Local development
1. Start the local server:
   python3 server.py
2. Open http://127.0.0.1:8000/
3. The frontend will call the local endpoint at http://127.0.0.1:8000/api/evaluate.json

## Cloudflare Workers deployment
1. Push this repository to GitHub.
2. Install Wrangler if needed: npm install -g wrangler
3. Log in: wrangler login
4. Deploy the Worker:
   wrangler deploy
5. After deployment, update the fallback endpoint in [frontend/script.js](frontend/script.js) to your Workers URL.

## Next step
Once the Worker is deployed, the frontend can call the real backend endpoint at:
- /api/health
- /api/evaluate