# Frontend implementation checklist (doc/frontend/frontend for gamefowl derby.md)

| Doc section | Requirement | Status |
|-------------|-------------|--------|
| **Home Screen** | Bold title "GAMEFOWL DERBY", stylized | ✅ `App.tsx` – `.game-title` |
| | Main menu: Enter Tournament, My Entry, The Keep, Leaderboards, Settings | ✅ Links when logged in |
| | Buttons large, polished, glow on hover | ✅ `.menu-btn` in App.css |
| | Two roosters, arena background, ambient audio/camera | ⚪ Not implemented (visual/audio polish) |
| **Enter Tournament** | Begins main gameplay | ✅ Links to `/tournaments` |
| **My Entry** | 20 breeds, image + short description | ✅ `/my-entry` – gallery + placeholder description |
| | Select up to 10 roosters (same or mixed) | ⚠️ Backend supports 1 entry per user per tournament; UI shows "1/10" and lineup bar |
| **The Keep** | Bench vs Flypen choice | ✅ On Enter flow + Home links to tournaments |
| **Leaderboards** | Top players, top breeds, seasonal rankings | ✅ Page at `/leaderboards` (placeholder until API) |
| **Settings** | Settings screen | ✅ Page at `/settings` (placeholder) |
| **Derby Types** | Four types with name + description | ✅ Long Heel, Short Heel, Pilipino, Mexican + descriptions |
| | Symbolic icon per derby | ⚪ Not implemented |
| | Entry fee in coins | ✅ "Entry fee: 10 coins" on tournament cards |
| | Prize tier (Standard, Grand, Prestigious) | ✅ "Prize tier: Standard" on cards |
| **Selecting the Entry** | Scrollable breed gallery | ✅ Grid on Enter + My Entry |
| | Breed card: name, large image, description, five qualities | ✅ Name, image, qualities; description on My Entry |
| | Five qualities: Power, Speed, Intelligence, Accuracy, Stamina | ✅ |
| | Entry Lineup Bar at bottom (selected birds) | ✅ "Roosters entered: 1/10" + breed name |
| **Selecting the Keep** | Bench / Flypen with descriptions | ✅ Radio options with full copy |
| **Dynamic Attribute Adjustment** | Attribute bars visibly shift (before/after) | ✅ Confirmation panel shows "Adjusted attributes" bars |
| **Derby Entry Confirmation** | Panel: Derby Name, Type, Entry Fee, Roosters (X/10), Keep Type | ✅ |
| | Buttons: Enter the Derby, Return to Selection | ✅ |
| | Coins deducted, entry locked on confirm | ✅ Backend |
| **Tournament Beginning** | Arena fade, crowd noise, banners, camera | ⚪ Not implemented (bracket is list view) |
| **Announcer Introduction** | Announcer text on screen | ⚪ Not implemented |
| **The Match** | Birds move, result screen, result text | ⚪ Match result as text in bracket only |
| **Experience Goal** | Dramatic, competitive, fast paced | ⚪ UX polish / future |

**Legend:** ✅ Done | ⚠️ Partial (backend or design constraint) | ⚪ Not implemented
