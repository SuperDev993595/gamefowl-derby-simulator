# Full Function Verification Checklist

Every backend function, API endpoint, and frontend usage is listed below. ✅ = implemented and wired. ⚠️ = implemented but not used in UI (optional).

---

## Backend: Auth (`app/auth.py`)

| Function | Purpose | Status |
|----------|---------|--------|
| `verify_password(plain, hashed)` | Check password against hash | ✅ Used in login |
| `get_password_hash(password)` | Hash password for storage | ✅ Used in register + seed_db |
| `create_access_token(data)` | Issue JWT (sub=user_id, exp) | ✅ Used in register + login |
| `get_current_user(credentials, db)` | Validate Bearer token, return User or None | ✅ Used by optional auth routes |
| `require_user(user)` | Raise 401 if no user | ✅ Used by /me, enter, admin |
| `require_admin(user)` | Raise 403 if not admin | ✅ Used by admin routes |

---

## Backend: Database (`app/database.py`)

| Function | Purpose | Status |
|----------|---------|--------|
| `get_db()` | Yield async session; commit on success, rollback on error | ✅ Injected into all routers |
| `init_db()` | Create all tables | ✅ Called in lifespan on startup |

---

## Backend: Seed (`app/seed_data.py`, `app/seed_db.py`)

| Function / Data | Purpose | Status |
|-----------------|---------|--------|
| `BREEDS` | 20 breeds + image filenames | ✅ Used in seed_db |
| `DERBY_TYPES` | long_heel, short_heel, long_blade, short_blade | ✅ Used in seed_db |
| `RATING_STRINGS` | 4 lists of "P.S.I.St.A" strings per derby type | ✅ Used in seed_db via get_rating_list |
| `get_rating_list(derby_index, breed_index)` | Parse string to [power, speed, intel, stamina, accuracy]; default accuracy for 4-value | ✅ Used in seed_db |
| `seed()` | Create tables, seed breeds+traits, seed admin user | ✅ Called in main lifespan |

---

## Backend: Tournament Engine (`app/services/tournament_engine.py`)

| Function | Purpose | Status |
|----------|---------|--------|
| `parse_rating_string(s)` | Parse "P.S.I.St.A" string (used in seed only; engine uses DB) | ✅ Exists; seed uses get_rating_list instead |
| `get_traits_for_breed_derby(db, breed_id, derby_type)` | Load (power, speed, intel, stamina, accuracy) from BreedTrait | ✅ Used in resolve_pending_matches_for_round |
| `resolve_match(power_a, power_b, seed)` | Weighted sum + randomness → 1 or 2 (A or B wins) | ✅ Used in resolve_pending_matches_for_round |
| `can_still_win(wins, losses, total_rounds, leader_wins)` | True if entry can still tie/beat leader | ✅ Used in mark_eliminated |
| `mark_eliminated(db, tournament_id, total_rounds)` | Set status=eliminated for entries that can’t catch leader | ✅ Called after each round in advance_tournament_round |
| `get_entries_for_round(db, tournament_id, round_number, is_tie_breaker)` | Round 1: all active (or tied leaders if tie-breaker); N>1: winners from round N−1 | ✅ Used in create_pairings_for_round |
| `create_pairings_for_round(...)` | Shuffle entries, pair 2-by-2; odd → BYE match, winner_entry_id set, wins+1 | ✅ Called in advance_tournament_round |
| `resolve_pending_matches_for_round(...)` | For each PENDING match, get traits, resolve_match, set winner, update wins/losses | ✅ Called in advance_tournament_round |
| `get_tied_leader_entries(db, tournament_id)` | Active entries with max wins, then min losses | ✅ Used for tie-breaker start and single-winner check |
| `advance_tournament_round(db, tournament)` | If scheduled rounds done: check ties → finish or start tie-breaker. Else: next_round, pair, resolve, eliminate, commit. Return event. | ✅ Called from admin advance_round |

---

## Backend: WebSocket Manager (`app/websocket_manager.py`)

| Method | Purpose | Status |
|--------|---------|--------|
| `subscribe_tournament(tournament_id, websocket)` | Add ws to tournament channel | ✅ Called in main websocket_tournament |
| `unsubscribe_tournament(tournament_id, websocket)` | Remove ws on disconnect | ✅ Called on WebSocketDisconnect |
| `broadcast_tournament(tournament_id, event, payload)` | Send JSON to all subscribers | ✅ Called in admin advance_round after round/tournament_finished |

---

## Backend: API Routers

### Auth (`/api/auth`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| POST | `/register` | Create user, return token + username + balance | ✅ Register page |
| POST | `/login` | Validate credentials, return token + username + balance | ✅ Login page |
| GET | `/me` | Return current user (id, username, email, balance, is_admin) | ✅ auth.tsx (fetchUser, refreshBalance) |

### Breeds (`/api/breeds`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| GET | `` | List all breeds with traits | ✅ EnterTournament page (breed grid) |

### Tournaments (`/api/tournaments`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| GET | `` | List tournaments (optional ?status=) | ✅ Tournaments, Admin |
| GET | `/{tournament_id}` | Get one tournament + entry_count | ✅ EnterTournament, Bracket |
| POST | `` | Create tournament (admin; name, derby_type, total_rounds, start_at) | ✅ Admin create |
| PATCH | `/{tournament_id}` | Update tournament (admin) | ⚠️ Not used in UI (API ready) |

### Entries (`/api/entries`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| POST | `/tournaments/{id}/enter` | Deduct tokens, create entry (breed_id) | ✅ EnterTournament Pay & Enter |
| GET | `/tournaments/{id}/standings` | Standings (entry_id, username, breed_name, wins, losses, status) | ✅ Bracket page |

### Matches (`/api/matches`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| GET | `/tournaments/{id}` | List matches for tournament (with entry usernames/breeds) | ✅ Bracket page |

### Admin (`/api/admin`)

| Method | Path | Purpose | Frontend usage |
|--------|------|---------|----------------|
| POST | `/tournaments/{id}/start` | Set status=running | ✅ Admin Start |
| POST | `/tournaments/{id}/advance-round` | Run advance_tournament_round; payout if finished; broadcast | ✅ Admin Advance round |
| POST | `/tournaments/{id}/restart` | Delete matches, reset entry stats, tournament to draft | ✅ Admin Restart |
| POST | `/tournaments/{id}/clone` | New tournament with same config | ✅ Admin Clone |

---

## Backend: Main (`app/main.py`)

| Item | Purpose | Status |
|------|---------|--------|
| Lifespan | init_db() + seed() on startup | ✅ |
| CORS | Allow frontend origin(s) from settings | ✅ |
| Routers | auth, breeds, tournaments, entries, matches, admin | ✅ All included |
| Static `/breed-pics` | Serve `resources/breed pics` | ✅ If folder exists |
| WebSocket `/ws/tournaments/{id}` | Accept, subscribe, receive loop, unsubscribe on disconnect | ✅ |
| GET `/health` | Health check | ✅ (no frontend use; for deployment) |

---

## Frontend: API & Auth

| Item | Purpose | Status |
|------|---------|--------|
| `api(path, options)` | fetch with Authorization Bearer, JSON; throw on !res.ok | ✅ Used by all pages + auth |
| `breedImageUrl(filename)` | `${API_BASE}/breed-pics/${filename}` | ✅ EnterTournament breed grid |
| AuthProvider | login, register, logout, refreshBalance; state: token, username, isAdmin, tokenBalance, user | ✅ Wraps app |
| useAuth() | Access state + login/register/logout/refreshBalance | ✅ All pages that need auth or balance |

---

## Frontend: Pages & Routes

| Route | Page | Functions used | Status |
|-------|------|----------------|--------|
| `/` | Home | useAuth; redirect to /tournaments if logged in | ✅ |
| `/login` | Login | login(email, password), navigate to / | ✅ |
| `/register` | Register | register(email, password), navigate to / | ✅ |
| `/tournaments` | Tournaments | GET /api/tournaments; Link enter, bracket, admin; logout | ✅ |
| `/enter/:id` | EnterTournament | GET tournament, GET breeds; POST enter; refreshBalance; breedImageUrl | ✅ |
| `/bracket/:id` | Bracket | GET tournament, matches, standings; WebSocket subscribe; refetch on message | ✅ |
| `/admin` | Admin | GET tournaments; POST create, start, advance-round, restart, clone; require admin | ✅ |

---

## Frontend: WebSocket

| Item | Purpose | Status |
|------|---------|--------|
| Bracket useEffect | Connect to `ws(s)://.../ws/tournaments/{id}` | ✅ |
| onmessage | Call fetchData() to refetch tournament, matches, standings | ✅ |
| Cleanup | Close ws, unsubscribe on unmount | ✅ |

---

## End-to-End Flows Verified

| Flow | Steps | Status |
|------|--------|--------|
| Register → see balance | Register → token stored → /me or token in response → state.tokenBalance | ✅ |
| Enter derby | Select tournament → Enter → select breed → Pay & Enter → tokens deducted, entry created | ✅ |
| Admin start → advance | Start → Advance round (pair round 1, resolve, eliminate) → repeat | ✅ |
| Tie-breaker | After last scheduled round, if tied → is_tie_breaker=True, round 1 = tied entries only → until one winner | ✅ |
| Winner payout | On tournament_finished, winner gets pool + bonus; broadcast sent | ✅ |
| Restart | Matches deleted, entries reset (wins/losses/status); tournament draft | ✅ |
| Clone | New tournament created; list refetched | ✅ |
| Bracket live update | Admin advances → backend broadcasts → Bracket ws.onmessage → fetchData | ✅ |

---

## Summary

- **All core functions are implemented and wired.**  
- **PATCH tournament** is implemented in the API but not used in the Admin UI (optional; e.g. for future “Edit tournament” or API clients).  
- **parse_rating_string** in the engine is unused (seed uses get_rating_list); harmless.  
- **Health** endpoint is for deployment checks; no frontend call.

No missing or broken functions for the current feature set.
