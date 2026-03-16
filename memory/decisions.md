# Architecture Decision Records (ADRs)

## ADR-001: Bot Framework — aiogram 3.x

**Status:** Accepted

**Context:** Need a Python Telegram bot framework for async workloads and multi-step FSM flows.

**Decision:** Use aiogram 3.x.

**Reasons:**
- Fully async (asyncio-native) — no threading hacks
- Built-in FSM for multi-step onboarding, /match, /dream, /palmreading, /sharecard
- Middleware support for future rate limiting
- python-telegram-bot is sync-first; telebot lacks FSM

**Consequences:** Handlers must be async. All blocking operations (Pillow, geocoding, kerykeion) run in `loop.run_in_executor`.

---

## ADR-002: Astrology Engine — kerykeion

**Status:** Accepted

**Context:** Need Vedic/sidereal natal chart calculations in pure Python.

**Decision:** Use kerykeion with `zodiac_type="Sidereal"`, `sidereal_mode="LAHIRI"`.

**Reasons:**
- Pure Python — no binary deps
- Supports natal charts, transits, house systems, aspects
- Lahiri ayanamsa is standard for Indian Vedic astrology
- flatlib is abandoned; astropy is astronomy not astrology

**Consequences:** Always pass `zodiac_type="Sidereal"` and `sidereal_mode="LAHIRI"` — never use tropical defaults.

---

## ADR-003: AI Provider — OpenRouter (not Anthropic direct)

**Status:** Accepted (changed from original Anthropic direct plan)

**Context:** Need cost-effective AI for high-volume text generation.

**Decision:** Use OpenRouter with `z-ai/glm-4.5-air:free` model via the `openai` SDK.

**Reasons:**
- Free tier sufficient for MVP and early growth
- OpenRouter gives access to many models — easy to upgrade per feature
- Same `openai` SDK interface — `base_url="https://openrouter.ai/api/v1"`
- GLM 4.5 Air produces good quality Vedic astrology text

**Critical:** GLM is a thinking model — always use `max_tokens=800`. Lower values produce truncated output.

**Consequences:** If rate limits hit, upgrade to a paid OpenRouter plan or switch per-feature model.

---

## ADR-004: Caching Strategy — Redis per sign per day

**Status:** Accepted

**Context:** Many users with same sun sign — calling AI for every /horoscope is wasteful.

**Decision:** Cache one reading per zodiac sign per language per calendar day.

**Key insight:** Horoscopes are sign-based. 12 signs × 2 languages = 24 AI calls/day max regardless of user count.

**Extended to:** Career (by lagna+dasha), marriage, wealth, spiritual, numerology (by name+DOB), milestones (by user, 7 days).

**Not cached:** /dream, /palmreading (user-unique), /ask (question-unique).

**TTL:** Seconds remaining until midnight UTC.

---

## ADR-005: Database — SQLite dev / PostgreSQL prod

**Status:** Accepted

**Context:** Need zero-config dev with production-grade prod.

**Decision:** SQLite for local dev, PostgreSQL for production, via SQLAlchemy 2.x async.

**Reasons:**
- SQLite: zero config, file-based
- PostgreSQL: production-grade, Railway plugin available
- Single codebase: swap `DATABASE_URL` env var

**Consequences:** No SQLite-specific SQL. Delete `astro.db` when adding new columns (no migration tooling).

---

## ADR-006: Deployment — Railway

**Status:** Accepted

**Context:** Need cheap deployment with managed Postgres + Redis.

**Decision:** Deploy on Railway.

**Reasons:**
- Git-push deploy
- Native Postgres and Redis plugins
- Free tier for MVP; hobby plan ($5/mo) for always-on

**Consequences:** Railway free tier sleeps on idle — use hobby plan for production.

---

## ADR-007: Image Generation — Pillow (not external image API)

**Status:** Accepted (Phase 8)

**Context:** Need shareable destiny report card and compatibility card images.

**Decision:** Generate images locally using Pillow.

**Reasons:**
- No external API cost or rate limit
- Full control over design
- Runs in thread executor (non-blocking)
- Fonts available at `/System/Library/Fonts/Supplemental/Arial*.ttf`

**Design:** 900×500px PNG. Dark cosmic theme (navy background, gold accents, white text).

**Consequences:** Image generation is CPU-bound — use `loop.run_in_executor(None, ...)` always.

---

## ADR-008: Palm Reading — Vision AI via OpenRouter

**Status:** Accepted (Phase 5)

**Context:** Palm reading requires image analysis.

**Decision:** Use `meta-llama/llama-3.2-11b-vision-instruct:free` via OpenRouter for palm photo analysis.

**Reasons:**
- Free vision model available on OpenRouter
- Supports base64 image input via openai SDK messages format
- Separate from main GLM model — palm_service.py has its own client

**Consequences:** Vision model may be less capable than paid alternatives. If quality is poor, upgrade to `google/gemini-flash-1.5` (paid).

---

## ADR-009: Scheduler — asyncio (not APScheduler)

**Status:** Accepted (Phase 7)

**Context:** Need cron-like scheduled pushes (daily horoscope, festival alerts, etc.).

**Decision:** Use plain `asyncio` background task with `asyncio.sleep(1800)` loop. No external scheduler library.

**Reasons:**
- APScheduler not in requirements — avoids new dependency
- Simple enough use case (4 check functions, every 30 min)
- Redis dedup keys prevent double-sends if bot restarts

**Consequences:** Not production-grade for high-precision timing. For sub-minute scheduling, add APScheduler later.

---

## ADR-010: i18n — Hybrid approach

**Status:** Accepted

**Context:** Phases 1–4 used `app/i18n.py` central string store. Phases 5–8 added many new commands.

**Decision:** Phases 1–4 strings live in `i18n.py` with `t(lang, key)` helper. Phases 5–8 handlers use inline `_STRINGS = {"en": {...}, "hi": {...}}` dicts.

**Reasons:**
- Avoids bloating i18n.py with 200+ keys
- Each handler is self-contained
- No functional difference for the bot

**Consequences:** Strings are split across files. If centralizing is needed, move all to i18n.py.
