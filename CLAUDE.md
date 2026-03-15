# CLAUDE.md — Agent Onboarding Guide

> Read this first. Current state, what's done, what's next, rules.

## What This Is

**Nakshatra Astro** — AI Vedic astrology Telegram bot (`@Nakshatra_Astrobot`).
Hindi + English. Vedic/sidereal calculations. Claude/OpenRouter AI readings.
Target: Indian astrology audience. Monetize via reports, remedies, puja bookings, subscriptions.

## Memory Index

| File | Read when... |
|---|---|
| [memory/project_summary.md](memory/project_summary.md) | Need goals, vision, target users |
| [memory/architecture.md](memory/architecture.md) | Touching any service, DB, or cache layer |
| [memory/decisions.md](memory/decisions.md) | Considering changing a library or pattern |
| [memory/requirements.md](memory/requirements.md) | Implementing a feature or fixing a bug |
| [memory/roadmap.md](memory/roadmap.md) | What's done and what's next |

## Current State (as of Phase 1 complete)

### What exists and works:
```
app/
├── bot.py                  — entry point, all routers wired, bot menu set
├── config.py               — pydantic-settings (.env)
├── database.py             — async SQLAlchemy, SQLite dev
├── i18n.py                 — all UI strings in en/hi
├── models/user.py          — User: name, gender, birth data, language,
│                             free_questions_used, subscription_tier
├── services/
│   ├── user.py             — get_or_create, update_birth_data, increment_questions
│   ├── astrology.py        — Vedic sidereal (Lahiri): Kundli, Nakshatra, Dasha, Panchang
│   ├── horoscope.py        — OpenRouter AI: horoscope, intro, ask_ai, spiritual_guidance
│   └── cache.py            — Redis cache, midnight UTC TTL
└── handlers/
    ├── start.py            — FSM: lang → name → gender → DOB → time → city → AI intro
    ├── horoscope.py        — /horoscope (Vedic, lucky num+color)
    ├── chart.py            — /kundli + /chart alias
    ├── panchang.py         — /panchang (Tithi, Nakshatra, Rahu Kaal, Abhijit)
    ├── ask.py              — /ask (3 free questions, paywall prompt after)
    ├── spiritual.py        — /spiritual (mantra + planet influence)
    └── sign.py             — /sign [zodiac]
```

### Bot commands registered:
`/start` `/horoscope` `/kundli` `/panchang` `/ask` `/spiritual` `/sign`

### Infrastructure:
- Python 3.13, aiogram 3.x, kerykeion (Vedic), OpenRouter GLM 4.5 Air (free)
- SQLite (dev), Redis FSM + cache
- GitHub: `zarvisaz007/nakshatra-astro-bot`
- Running locally on Mac via `venv/bin/python -m app.bot`

## What To Build Next — Phase 2

**No payment module** (skip entirely for now).

Build in this order:

1. **Admin UI** (`app/admin/`) — FastAPI web panel (localhost:8080)
   - Change API keys, model, view user stats, manage settings
   - Simple HTML + password-protected
   - Run alongside bot as separate process

2. **Kundli Matching** (`/match`) — Guna Milan, compatibility score, Manglik check

3. **Dosha Detection** (`/dosha`) — Manglik, Kaal Sarp, Shani, Rahu-Ketu, Pitru

4. **Lucky Name & Number** (`/lucky`) — baby names, business name, lucky numbers

5. **Personal Remedies** (`/remedy`) — mantra, donation, fasting, temple recommendation

See `memory/roadmap.md` for full checklist.

## Stack Quick Reference

```
Bot:        aiogram 3.x (async, FSM)
Astrology:  kerykeion — zodiac_type="Sidereal", sidereal_mode="LAHIRI"
AI:         OpenRouter via openai SDK — base_url="https://openrouter.ai/api/v1"
Model:      z-ai/glm-4.5-air:free (max_tokens=800, thinking model needs headroom)
Cache:      Redis — key: horoscope:{sign}:{lang}:{YYYY-MM-DD}, TTL=midnight UTC
DB:         SQLAlchemy async, SQLite dev / Postgres prod
Config:     pydantic-settings → .env
Admin:      FastAPI + Jinja2, localhost:8080, basic auth
```

## Critical Rules

- **Async everywhere** — no blocking calls in handlers
- **Cache before AI** — always check Redis before calling OpenRouter
- **Thin handlers** — logic in services/, handlers just orchestrate
- **No payment module** — skip Razorpay/Stripe until explicitly asked
- **GLM needs 800 max_tokens** — it's a thinking model; 300 leaves nothing for output
- **Vedic only** — zodiac_type="Sidereal", sidereal_mode="LAHIRI" always
- **Delete astro.db when adding new columns** — no migration tooling yet

## Environment Variables

```
TELEGRAM_BOT_TOKEN=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=z-ai/glm-4.5-air:free
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./astro.db
ADMIN_PASSWORD=changeme
ADMIN_PORT=8080
```

## Running Locally

```bash
# Terminal 1 — bot
cd ~/Desktop/claude-terminal
brew services start redis
venv/bin/python -m app.bot

# Terminal 2 — admin UI (Phase 2)
venv/bin/python -m app.admin
```

## After Completing Work

1. Check off items in `memory/roadmap.md`
2. Add ADRs to `memory/decisions.md` for significant choices
3. Commit with `feat:` / `fix:` / `chore:` prefix
4. Push to `zarvisaz007/nakshatra-astro-bot`
