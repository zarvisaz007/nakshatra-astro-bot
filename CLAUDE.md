# CLAUDE.md — Agent Onboarding Guide

> Read this first. It tells you what this project is, what's been done, what to do next, and how to work here.

## What This Is

An astrology Telegram bot. Users send their birth data, get AI-generated daily horoscopes (Claude-powered, Redis-cached) and natal chart summaries (kerykeion).

## Project Memory

All deep context lives in `memory/`. Read these before making decisions:

| File | Read when... |
|---|---|
| [memory/project_summary.md](memory/project_summary.md) | You need to understand goals, scope, target users |
| [memory/architecture.md](memory/architecture.md) | You're touching any service, DB, or cache layer |
| [memory/decisions.md](memory/decisions.md) | You're considering changing a library or pattern |
| [memory/requirements.md](memory/requirements.md) | You're implementing a feature or fixing a bug |
| [memory/roadmap.md](memory/roadmap.md) | You need to know what's done and what's next |

## Current State

**Phase 1 bootstrap is complete.** The repo has docs/architecture only — no application code yet.

What exists:
- `README.md`, `.gitignore`, `MEMORY.md`, `CLAUDE.md`
- `memory/` — full architecture, decisions, requirements, roadmap

What does NOT exist yet (needs to be built):
- `app/` — all application code
- `requirements.txt`
- `.env.example`

## What To Build Next

Work through **Phase 1** in `memory/roadmap.md` in this order:

1. `requirements.txt` + `.env.example`
2. `app/config.py` — pydantic-settings
3. `app/models/user.py` — SQLAlchemy User model
4. `app/services/astrology.py` — kerykeion natal chart
5. `app/services/horoscope.py` — Claude API reading
6. `app/services/cache.py` — Redis TTL cache
7. `app/handlers/start.py` — onboarding FSM
8. `app/handlers/horoscope.py`
9. `app/handlers/chart.py`
10. `app/handlers/sign.py`
11. `app/bot.py` — entry point

## Stack (Quick Reference)

```
Bot:        aiogram 3.x (async, FSM built-in)
Astrology:  kerykeion (pure Python, natal + transits)
AI:         Claude API — claude-haiku-4-5 (cheap, fast)
Cache:      Redis — key: horoscope:{sign}:{YYYY-MM-DD}, TTL = seconds to midnight UTC
DB:         SQLite (dev) / PostgreSQL (prod) via SQLAlchemy async
Deploy:     Railway (git-push, Postgres + Redis plugins)
```

## Coding Conventions

- All async — no blocking calls anywhere in the bot process
- Config via environment variables only (pydantic-settings), never hardcode
- SQLAlchemy async sessions — always use `async with session` context manager
- Redis keys follow the convention in `memory/architecture.md`
- Structured logging (standard `logging` module, JSON formatter for prod)
- Keep handlers thin — business logic lives in `app/services/`

## Environment Variables (required)

```
TELEGRAM_BOT_TOKEN=
ANTHROPIC_API_KEY=
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./astro.db
```

## Do Not

- Do not change the framework choices without reading `memory/decisions.md` first
- Do not call Claude API per-user for horoscopes — always go through the Redis cache
- Do not use sync SQLAlchemy — async only
- Do not store secrets in code — `.env` only
- Do not add features beyond the current phase without updating `memory/roadmap.md`

## When You Finish Work

Update `memory/roadmap.md` — check off completed items and note any new decisions made. If you made a significant architectural choice, add an ADR to `memory/decisions.md`.
