# project-invent-ai-reviewer

## Overview
A simple demo app with:
- a frontend upload UI
- a mock backend endpoint for evaluation results
- a Vercel-ready API structure for future LLM integration

## Local development
1. Start the local server:
   python3 server.py
2. Open http://127.0.0.1:8000/
3. The frontend will call the local endpoint at http://127.0.0.1:8000/api/evaluate.json

## Vercel deployment
1. Push this repository to GitHub.
2. Open Vercel and import the repository.
3. Vercel should detect the Vercel config in [vercel.json](vercel.json).
4. Deploy the project.
5. After deployment, update the frontend endpoint in [frontend/script.js](frontend/script.js) if the generated Vercel URL differs from the fallback value.

## Next step
Once the Vercel deployment is live, the frontend can call the real backend endpoint at:
- /api/health
- /api/evaluate