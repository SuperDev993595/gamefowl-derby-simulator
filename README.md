# Gamefowl Derby Simulator

Browser-based tournament simulator: players choose a breed (rooster), pay tokens, and enter a derby. Rounds are run with winners advancing; tie-breakers decide a single winner. Admin can create/start/advance/restart/clone tournaments.

## Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2 (async), SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React 18, TypeScript, Vite, React Router
- **Auth:** JWT (email/password) and optional **Google SSO**. Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` to enable "Sign in with Google"; no local password is stored for SSO users.

## Quick start

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed (SECRET_KEY, DATABASE_URL for PostgreSQL)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

On first run, the app creates the DB, seeds 20 breeds with trait ratings, and a default admin user:

- **Admin:** `admin@example.com` / `admin123`

### 2. Frontend

```bash
cd client
npm install
npm run dev
```

- App: http://localhost:5173  

Set `VITE_API_URL=http://localhost:8000` in `client/.env` if the API is not on that URL.

### 3. Play flow

1. **Register** or **Sign in** (email/password or **Sign in with Google** if configured).
2. **Derbies:** List tournaments (each has derby type, prize tier, entry fee). **Enter** → select 1–10 roosters (same or mixed breeds), choose **Keep** (Bench or Flypen), review adjusted attributes → **Enter the Derby** (tokens deducted).
3. **Bracket:** View standings and matches; for played matches, **View match** opens the arena view with announcer and result.
4. **Leaderboards:** Top players, top breeds, seasonal (last 30 days). **Settings:** Sound and reduce motion.
5. **Admin:** Sign in as `admin@example.com` → **Admin** → Create tournament (name, derby type, 10–20 rounds, optional **start date/time**, **prize tier**: Standard / Grand / Prestigious) → **Start** → **Advance round** repeatedly. Tie-breakers run until one winner; winner receives token pool + tier bonus. **Restart** or **Clone** as needed.

## Config (backend `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./derby.db` | Use `postgresql+asyncpg://...` for production |
| `SECRET_KEY` | (dev default) | Change in production |
| `ENTRY_COST_TOKENS` | 10 | Legacy; use tier costs below |
| `entry_cost_standard` | 10 | Entry cost (Standard tier) |
| `entry_cost_grand` | 25 | Entry cost (Grand tier) |
| `entry_cost_prestigious` | 50 | Entry cost (Prestigious tier) |
| `winner_bonus_standard` / `_grand` / `_prestigious` | 50 / 150 / 300 | Winner bonus on top of pool |
| `STARTING_TOKENS` | 100 | New user balance |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated frontend origins |
| `GOOGLE_CLIENT_ID` | — | Optional; enables "Sign in with Google" |
| `GOOGLE_CLIENT_SECRET` | — | Optional |
| `GOOGLE_REDIRECT_URI` | — | e.g. `http://localhost:5173/auth/callback` |

## Derby types & breeds

- **Derby types:** Long Heel, Short Heel, Pilipino, Mexican (with attribute modifiers per `doc/frontend/Derby Attribute.md`).
- **Breeds:** 20 (Hatch, Kelso, Claret, etc.) with short descriptions. Trait ratings (Power, Speed, Intelligence, Stamina, Accuracy) per breed per derby type. **Keep** (Bench / Flypen) further adjusts attributes before each match.
- **Breed images:** Served from `resources/breed pics/` at `/breed-pics/`.

## Build for production

**Backend:** Use a process manager (e.g. Gunicorn with uvicorn worker) and a production ASGI host. Point `DATABASE_URL` to PostgreSQL.

**Frontend:**

```bash
cd client
npm run build
```

Serve the `dist/` folder with your web server or static host; set `VITE_API_URL` to your API base URL.

## Project layout

```
backend/
  app/
    main.py          # FastAPI app, CORS, WebSocket, static mount
    config.py        # Settings
    database.py      # Async SQLAlchemy engine/session
    models.py        # User, Breed, BreedTrait, Tournament, Entry, Match
    auth.py          # JWT, password hash, get_current_user, require_admin
    schemas.py       # Pydantic request/response
    seed_data.py     # Breed names + trait rating strings
    seed_db.py       # Seed breeds, traits, default admin
    websocket_manager.py  # Broadcast to tournament subscribers
    routers/         # auth, breeds, tournaments, entries, matches, admin
    services/
      tournament_engine.py  # Pairing, match resolution, elimination, tie-breakers
client/
  src/
    api.ts           # fetch wrapper, types
    auth.tsx         # Auth context (login, register, logout)
    App.tsx, main.tsx
    pages/           # Login, Register, Tournaments, EnterTournament, Bracket, Admin
doc/                 # PROJECT_ANALYSIS.md, IMPLEMENTATION_GUIDE.md
resources/breed pics/  # Breed images
```

## User guide (short)

- **Sign up / Sign in:** Register with email/password, or use **Sign in with Google** (if enabled). You receive an autogenerated username (e.g. `player_xxxx`); admin seed is `admin`.
- **Join a derby:** **Derbies** → pick a tournament (draft/scheduled) → **Enter this derby** → select 1–10 roosters (click breeds to add to lineup; remove with ×), choose **The Keep** (Bench or Flypen), **Review entry** → **Enter the Derby**. Tokens are deducted by prize tier (Standard 10, Grand 25, Prestigious 50 coins).
- **Tie-breakers:** After the last scheduled round, if two or more are tied for first, the system runs tie-breaker rounds among them until one winner remains. That winner gets the full token pool (sum of entry fees) plus the tier bonus.
- **Admin:** Create tournament (name, derby type, 10–20 rounds, optional start date/time, prize tier). **Start** → **Advance round** for each round. **Restart** clears matches and resets entry stats; **Clone** creates a new tournament with the same config.
