# CLAUDE.md — Agent Onboarding Guide

> Read this first. Current state, all rules, what's done, what's next.

## What This Is

**Nakshatra Astro** — AI Vedic astrology Telegram bot (`@Nakshatra_Astrobot`).
Hindi + English. Vedic/sidereal (Lahiri) calculations via kerykeion. OpenRouter GLM AI readings.
Target: Indian astrology audience on Telegram.

**GitHub:** `zarvisaz007/nakshatra-astro-bot`
**Local dir:** `~/Desktop/claude-terminal`

---

## Memory Index

| File | Read when... |
|---|---|
| [memory/project_summary.md](memory/project_summary.md) | Need goals, vision, target users |
| [memory/architecture.md](memory/architecture.md) | Touching any service, DB, cache, or adding new feature |
| [memory/decisions.md](memory/decisions.md) | Considering changing a library or pattern |
| [memory/requirements.md](memory/requirements.md) | Implementing a feature or fixing a bug |
| [memory/roadmap.md](memory/roadmap.md) | What's done and what's next |

---

## Current State — Phases 1–5, 7, 8 Complete

### All 24 Bot Commands

| Command | Phase | Description |
|---------|-------|-------------|
| /start | 1 | Onboarding FSM: lang → name → gender → DOB → time → city → AI intro |
| /horoscope | 1 | Vedic daily horoscope with lucky number + color |
| /kundli | 1 | Full birth chart (lagna, rashi, nakshatra, planets, dasha) |
| /panchang | 1 | Today's Tithi, Nakshatra, Rahu Kaal, Abhijit Muhurat |
| /ask | 1 | AI Q&A with kundli context (3 free questions) |
| /spiritual | 1 | Daily mantra + planet influence |
| /sign | 1 | Zodiac sign info (no account needed) |
| /match | 2 | Guna Milan compatibility (0–36 score) |
| /dosha | 2 | Manglik, Kaal Sarp, Shani, Pitru dosha detection |
| /lucky | 2 | Lucky numbers, colors, gemstones, name letters |
| /remedy | 2 | Mantra, donation, fasting, dasha remedy |
| /career | 3 | 10th house career analysis + AI reading |
| /marriage | 3 | 7th house marriage prediction + AI reading |
| /wealth | 3 | 2nd/11th house wealth analysis + AI reading |
| /dasha | 3 | Vimshottari Dasha timeline (current + next 5 periods) |
| /puja | 4 | Dasha-based puja + Navagraha special pujas + AI reading |
| /mantra | 4 | Nakshatra beeja mantra + dasha mantra + sadhana tips |
| /gems | 4 | Lagna lord primary gem + supporting gems + gems to avoid |
| /numerology | 5 | Chaldean numerology (Life Path, Destiny, Soul Urge) + AI |
| /dream | 5 | Vedic dream interpretation (FSM, AI) |
| /palmreading | 5 | Photo upload → vision AI palm reading |
| /notifications | 7 | Toggle daily notification opt-in (default: on) |
| /reportcard | 8 | Shareable destiny card image (Pillow, 900×500) |
| /sharecard | 8 | Shareable compatibility card image (FSM, score bar) |
| /milestones | 8 | Life milestones + dasha age timeline + AI forecast |

### Admin UI
- FastAPI web panel at `localhost:8080`
- Run: `venv/bin/python -m app.admin`
- Login password in `.env` as `ADMIN_PASSWORD`

---

## Full File Structure

```
app/
├── bot.py                      — entry point: all 24 routers wired, bot menu, scheduler start
├── config.py                   — pydantic-settings (.env)
├── database.py                 — async SQLAlchemy, SQLite dev / Postgres prod
├── i18n.py                     — UI strings for Phases 1–4 (en/hi); Phases 5–8 use inline dicts
├── admin/
│   ├── __main__.py
│   └── app.py                  — FastAPI admin UI (localhost:8080)
├── models/
│   └── user.py                 — User: name, gender, birth data, lang, free_questions_used,
│                                  subscription_tier, notifications_enabled
├── services/
│   ├── user.py                 — get_or_create, update_birth_data, increment_questions
│   ├── astrology.py            — Vedic sidereal (Lahiri): Kundli, Nakshatra, Dasha, Panchang
│   ├── horoscope.py            — OpenRouter AI: all AI calls via _call_ai(), prompts for all features
│   ├── cache.py                — Redis get/set, midnight UTC TTL helper
│   ├── vedic.py                — guna_milan, detect_doshas
│   ├── gems_service.py         — gem_recommendation, get_gems_reading
│   ├── puja_service.py         — puja recommendations
│   ├── mantra_service.py       — mantra + sadhana
│   ├── numerology_service.py   — Chaldean calc: get_numerology_profile, get_numerology_reading
│   ├── dream_service.py        — interpret_dream (AI, no cache)
│   ├── palm_service.py         — get_palm_reading (vision AI, llama-3.2-11b-vision:free)
│   ├── card_service.py         — generate_report_card + generate_compatibility_card (Pillow)
│   ├── milestones_service.py   — dasha age timeline + get_milestones_reading (7-day cache)
│   └── scheduler.py            — run_scheduler(): daily horo push, transit alerts, festivals, weekly
└── handlers/
    ├── start.py                — FSM onboarding
    ├── horoscope.py            — /horoscope
    ├── chart.py                — /kundli + /chart alias
    ├── sign.py                 — /sign
    ├── panchang.py             — /panchang
    ├── ask.py                  — /ask (3 free)
    ├── spiritual.py            — /spiritual
    ├── match.py                — /match (FSM, geocoding)
    ├── dosha.py                — /dosha
    ├── lucky.py                — /lucky
    ├── remedy.py               — /remedy
    ├── career.py               — /career
    ├── marriage.py             — /marriage
    ├── wealth.py               — /wealth
    ├── dasha.py                — /dasha
    ├── puja.py                 — /puja
    ├── mantra.py               — /mantra
    ├── gems.py                 — /gems
    ├── numerology.py           — /numerology
    ├── dream.py                — /dream (FSM)
    ├── palm.py                 — /palmreading (FSM, photo upload)
    ├── notifications.py        — /notifications (inline toggle)
    ├── reportcard.py           — /reportcard (Pillow image)
    ├── sharecard.py            — /sharecard (FSM, Pillow image)
    └── milestones.py           — /milestones
```

---

## Stack Quick Reference

```
Bot:          aiogram 3.x (async, FSM)
Astrology:    kerykeion — zodiac_type="Sidereal", sidereal_mode="LAHIRI" ALWAYS
AI (text):    OpenRouter via openai SDK — base_url="https://openrouter.ai/api/v1"
AI model:     z-ai/glm-4.5-air:free — max_tokens=800 (thinking model needs headroom)
AI (vision):  meta-llama/llama-3.2-11b-vision-instruct:free — for /palmreading
Cache:        Redis — key patterns documented in memory/architecture.md
DB:           SQLAlchemy async, SQLite dev / Postgres prod
Config:       pydantic-settings → .env
Admin:        FastAPI + Jinja2, localhost:8080, basic auth
Images:       Pillow — fonts at /System/Library/Fonts/Supplemental/Arial*.ttf
Scheduler:    asyncio background task (run_scheduler in services/scheduler.py)
```

---

## Critical Rules — NEVER BREAK THESE

- **Vedic only** — `zodiac_type="Sidereal"`, `sidereal_mode="LAHIRI"` always, no exceptions
- **Async everywhere** — no blocking calls in handlers; Pillow drawing runs in `loop.run_in_executor`
- **Cache before AI** — always check Redis before calling OpenRouter
- **Thin handlers** — logic in services/, handlers just orchestrate
- **No payment module** — skip Razorpay/Stripe until explicitly asked
- **GLM needs 800 max_tokens** — it's a thinking model; less leaves nothing for output
- **Delete astro.db when adding new columns** — no migration tooling
- **i18n.py** — only Phases 1–4 strings live here; newer handlers use inline `_STRINGS` dicts
- **No vector DB needed** — this bot does not need semantic search

---

## Environment Variables

```
TELEGRAM_BOT_TOKEN=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=z-ai/glm-4.5-air:free
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./astro.db
ADMIN_PASSWORD=nakshatra_admin
ADMIN_PORT=8080
```

---

## Running Locally

```bash
cd ~/Desktop/claude-terminal
brew services start redis
rm astro.db          # only needed if DB schema changed
venv/bin/python -m app.bot        # Terminal 1 — bot + scheduler (background)
venv/bin/python -m app.admin      # Terminal 2 — http://localhost:8080
```

Bot log: `/tmp/nakshatra_bot.log` if started with `> /tmp/nakshatra_bot.log 2>&1 &`

---

## Scheduler (Phase 7) — Background Task

Started automatically in `bot.py` via `asyncio.create_task(run_scheduler(bot))`.
Runs every 30 minutes. Sends:
- **Daily horoscope** at 01:30 UTC (7 AM IST) to opted-in users
- **Moon transit alerts** when nakshatra changes
- **Festival reminders** 1 day before major Hindu festivals + Ekadashi
- **Weekly digest** every Monday at 05:00 UTC

Redis dedup keys all prefixed `sched:` to avoid collision.

---

## Caching Strategy Summary

| Command | Cache key | TTL |
|---------|-----------|-----|
| /horoscope | `horoscope:{sign}:{lang}:{date}` | Until midnight UTC |
| /career | `career:{lagna}:{dasha}:{lang}` | Until midnight UTC |
| /marriage | `marriage:{lagna}:{dasha}:{lang}` | Until midnight UTC |
| /wealth | `wealth:{lagna}:{dasha}:{lang}` | Until midnight UTC |
| /spiritual | `spiritual:{moon_sign}:{lang}` | Until midnight UTC |
| /numerology | `numerology:{name}:{dob}:{lang}` | Until midnight UTC |
| /milestones | `milestones:{telegram_id}:{lang}` | 7 days |
| /dream | No cache | Per call |
| /palmreading | No cache | Per call |

---

## What's Next — Phase 6 (Subscriptions)

```
- Basic ₹199/month  — unlimited /ask questions
- Premium ₹499/month — all basic + priority AI + PDF reports
- Elite ₹999/month  — all premium + personal astrologer chat
- Feature gates by subscription_tier (column already in User model)
- Payment via Razorpay (preferred for India) or Stripe
```

The `subscription_tier` column already exists on `User` model (`free/basic/premium/elite`).
The `/ask` handler already checks `u.subscription_tier` for unlimited questions.
All that's needed: payment webhook + tier upgrade logic.

---

## After Completing Work

1. Check off items in `memory/roadmap.md`
2. Add ADRs to `memory/decisions.md` for significant choices
3. Update this file's "Current State" section if new phases are added
4. Commit: `feat:` / `fix:` / `chore:` prefix
5. Push to `zarvisaz007/nakshatra-astro-bot`
6. Restart bot: `pkill -f app.bot && rm astro.db && venv/bin/python -m app.bot &`
