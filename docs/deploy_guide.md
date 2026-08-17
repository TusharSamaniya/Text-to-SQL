# 🚀 Deployment Guide — Text-to-SQL

The app in production has two pieces:

```
Flask API  →  Render      (always-on web service — sessions & long requests work)
React UI   →  Vercel      (static hosting — Vercel's home turf)
```

> Why not the API on Vercel? Serverless functions have a hard time cap
> (10s default, ~60s max free) and are stateless per invocation — our
> clarification engine needs in-memory sessions and multi-step Gemini
> calls that routinely exceed those limits. Render's always-on service
> has neither problem.

---

## Part 1 — Push to GitHub (you do this part)

Everything deployable is ready in the repo. From the project root:

```bash
git add .
git commit -m "Phase 5: deployment prep (render.yaml, waitress, VITE_API_URL)"
git push origin main
```

(Secrets are safe: `.env` is gitignored. `.env.example` and `render.yaml`
contain only placeholders.)

---

## Part 2 — Deploy the Flask API (Render)

1. Create a free account at https://render.com
2. **New → Blueprint** → connect GitHub → select this repo
3. Render reads `render.yaml` automatically and creates the service
4. Before first deploy completes, set the **secret env vars** in the
   service's dashboard (Render → your service → **Environment**):
   | Key | Value |
   |---|---|
   | `DATABASE_URL` | your Neon URL, e.g. `postgresql://neondb_owner:...@ep-...neon.tech/neondb?sslmode=require` |
   | `GEMINI_API_KEY` | your AIza/Google key |
   | `MODEL_NAME` | `gemini-flash-lite-latest` (already defaulted) |
5. Deploy → wait for **Live** → open `https://your-api.onrender.com/api/health`
   → you should see `{"status":"ok"}`

**How it works:** Render's start command is
`waitress-serve --port $PORT app:app` — the same production server we
verified locally. `rootDir: backend` tells Render the app lives in
`backend/`.

---

## Part 3 — Deploy the React frontend (Vercel)

1. Create a free account at https://vercel.com
2. **Add New → Project** → import the same GitHub repo
3. Vercel auto-detects Vite:
   - Framework preset: **Vite**
   - Build command: `npm run build`
   - Output directory: `dist`
4. **Before deploying, set the env var** (Vercel → Project → Settings →
   Environment Variables):
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://your-api.onrender.com/api/ask` |

   > `VITE_API_URL` is baked in at build time — it must point at your
   > deployed Render API. (In dev, the Vite proxy handled `/api`.)
5. Deploy → open the Vercel URL → ask a question!

`vercel.json` in the repo contains an SPA rewrite so the app works at
any route.

---

## Part 4 — Verify the full chain (the happy path)

1. Open the **Vercel** URL in a browser
2. Ask: `How many customers live in Mumbai?` → expect `7`
3. Ask: `Show me last month's best customers` → expect the clarification
   dialog → pick an option → expect a table of customers
4. Click **"🔍 Show the generated SQL"** — the query ran against your
   Neon cloud database on Render's server

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Could not reach the server` in the UI | `VITE_API_URL` missing/wrong → rebuild after fixing |
| Render health check failing | `DATABASE_URL` or `GEMINI_API_KEY` not set → check Environment tab |
| `429`/`503` errors on answers | Gemini free-tier rate limit — wait ~30s and retry |
| Clarification "forgets" the question | Only happens if the service restarted mid-dialog — Render free tier sleeps the service after ~15 min idle; first request wakes it (slow but fine) |

---

## Costs (all free tier)

- **Neon**: free Postgres (project paused after ~5 days idle — wake it from
  the dashboard before demoing)
- **Render**: free web service (goes to sleep ~15 min idle — first request
  after sleep takes ~30–60s to wake; this is normal)
- **Vercel**: free static hosting
- **Gemini**: free tier (~15–20 requests/min) — fine for a team demo
