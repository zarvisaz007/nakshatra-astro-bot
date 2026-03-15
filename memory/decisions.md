# Architecture Decision Records (ADRs)

## ADR-001: Bot Framework — aiogram 3.x

**Status:** Accepted

**Context:** Need a Python Telegram bot framework that handles long-running async workloads without blocking.

**Decision:** Use aiogram 3.x.

**Reasons:**
- Fully async (asyncio-native) — no threading hacks
- Built-in FSM (Finite State Machine) for multi-step onboarding flow
- Middleware support for auth, rate limiting, error handling
- Active maintenance, good community, modern API design
- python-telegram-bot is sync-first; telebot lacks FSM; aiogram wins on all counts

**Consequences:** Team must be comfortable with async Python. aiogram 3.x has breaking changes from 2.x — follow 3.x docs only.

---

## ADR-002: Astrology Engine — kerykeion

**Status:** Accepted

**Context:** Need to calculate natal charts, sun signs, planetary positions, and aspects from birth data.

**Decision:** Use kerykeion.

**Reasons:**
- Pure Python — no binary deps (no Swiss Ephemeris C library to compile)
- Supports natal charts, transits, aspects, house systems
- Actively maintained, pip-installable, works on Railway without buildpacks
- flatlib is abandoned; astropy is overkill (astronomy, not astrology)

**Consequences:** kerykeion requires internet access on first run to download ephemeris data. Bundle or pre-download for production.

---

## ADR-003: AI Readings — Claude API (claude-haiku-4-5)

**Status:** Accepted

**Context:** Need to generate horoscope text that feels personal and high-quality, not canned.

**Decision:** Use Claude API with claude-haiku-4-5 model.

**Reasons:**
- claude-haiku-4-5 is the fastest and cheapest Claude model — ideal for short text generation
- Anthropic prompt caching reduces cost further for repeated system prompts
- Output quality far exceeds template-based approaches
- OpenAI GPT-4o-mini is comparable but Anthropic is the operator's preference

**Consequences:** API key required. Cost scales with unique sign×day combinations (max 12/day). Monitor usage via Anthropic console.

---

## ADR-004: Caching Strategy — Redis per sign per day

**Status:** Accepted

**Context:** With many users, calling Claude for every `/horoscope` request would be expensive and slow.

**Decision:** Cache one reading per zodiac sign per calendar day in Redis.

**Key insight:** Horoscopes are sign-based, not user-specific. 12 signs × 1 Claude call/day = 12 API calls maximum per day, regardless of user count.

**TTL:** Seconds remaining until midnight UTC (reading expires at day rollover).

**Key format:** `horoscope:{sign}:{YYYY-MM-DD}`

**Consequences:** All users of the same sign get the same reading on a given day (acceptable for daily horoscopes). User-specific readings (e.g., natal chart transits) are NOT cached here.

---

## ADR-005: Database — SQLite dev / PostgreSQL prod

**Status:** Accepted

**Context:** Need persistent storage for user birth data. Dev must be zero-config.

**Decision:** SQLite for local dev, PostgreSQL for production, via SQLAlchemy async.

**Reasons:**
- SQLite: zero config, file-based, perfect for solo dev
- PostgreSQL: Railway plugin, free tier, production-grade
- SQLAlchemy 2.x async: single codebase works with both via swapping DATABASE_URL
- aiosqlite (dev) / asyncpg (prod) as drivers

**Consequences:** Never use SQLite-specific SQL. Test with both drivers before prod deploy.

---

## ADR-006: Deployment — Railway

**Status:** Accepted

**Context:** Need cheap, simple deployment with managed Postgres and Redis.

**Decision:** Deploy on Railway.

**Reasons:**
- Git-push deploy (no Dockerfile required for basic Python)
- Native Postgres and Redis plugins (add in one click)
- Free tier sufficient for MVP
- Fly.io is the backup if Railway limits hit

**Consequences:** Railway free tier has sleep-on-idle behavior. Upgrade to hobby plan ($5/mo) for always-on production use.
