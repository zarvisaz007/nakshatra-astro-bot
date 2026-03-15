# AGENTS.md — Multi-Agent Collaboration Guide

> For AI agents (Codex, Devin, Cursor, Copilot Workspace, etc.) working on this project.
> Also read: CLAUDE.md for full onboarding context.

## Project Snapshot

**Astrology Telegram Bot** — Python, aiogram 3.x, kerykeion, Claude API, Redis, SQLAlchemy async.

**Bootstrap complete. No application code exists yet.** All files in `memory/` are specs and design docs, not implemented features.

## Repository Layout

```
claude-terminal/
├── CLAUDE.md          ← Full agent onboarding (read this too)
├── AGENTS.md          ← This file
├── MEMORY.md          ← Index of memory/ docs
├── README.md          ← Human-facing overview
├── .gitignore
└── memory/
    ├── project_summary.md   ← Goals, scope, users
    ├── architecture.md      ← Stack + ASCII data flow diagrams
    ├── decisions.md         ← ADRs (why each technology was chosen)
    ├── requirements.md      ← Functional + non-functional requirements
    └── roadmap.md           ← Phase 1 checklist → Phase 2 → Phase 3
```

## Task Queue (Phase 1 — do these in order)

- [ ] `requirements.txt` — pinned deps (aiogram, kerykeion, anthropic, sqlalchemy, aiosqlite, asyncpg, redis, pydantic-settings)
- [ ] `.env.example` — template with all required vars
- [ ] `app/__init__.py`
- [ ] `app/config.py` — pydantic-settings, reads from .env
- [ ] `app/database.py` — async engine + session factory
- [ ] `app/models/__init__.py`
- [ ] `app/models/user.py` — User SQLAlchemy model
- [ ] `app/services/__init__.py`
- [ ] `app/services/cache.py` — Redis get/set with midnight TTL
- [ ] `app/services/astrology.py` — kerykeion: sun sign from DOB, natal chart text
- [ ] `app/services/horoscope.py` — Claude API call, uses cache service
- [ ] `app/handlers/__init__.py`
- [ ] `app/handlers/start.py` — aiogram FSM onboarding (collect DOB, time, location)
- [ ] `app/handlers/horoscope.py` — /horoscope command
- [ ] `app/handlers/chart.py` — /chart command
- [ ] `app/handlers/sign.py` — /sign [zodiac] command
- [ ] `app/bot.py` — entry point: dispatcher + router wiring, startup/shutdown hooks

## Key Interfaces to Implement

### HoroscopeService
```python
async def get_reading(sign: str, date: date) -> str:
    # 1. Check Redis: horoscope:{sign}:{date}
    # 2. Cache hit → return
    # 3. Cache miss → call Claude claude-haiku-4-5
    # 4. Store in Redis with TTL = seconds until midnight UTC
    # 5. Return reading
```

### AstrologyService
```python
def get_sun_sign(birth_date: date) -> str: ...
def get_natal_chart(birth_date: date, birth_time: time | None, lat: float, lon: float) -> str: ...
```

### UserService
```python
async def get_or_create(telegram_id: int) -> User: ...
async def update_birth_data(telegram_id: int, **kwargs) -> User: ...
```

## Constraints

- **Async everywhere** — aiogram 3.x requires it; no `asyncio.run()` inside handlers
- **Cache before Claude** — never call Claude without checking Redis first
- **Thin handlers** — handlers call services, services contain logic
- **Environment config only** — all secrets/config via pydantic-settings from `.env`

## After Completing Work

1. Check off completed items in `memory/roadmap.md`
2. If you made a tech decision not covered in `memory/decisions.md`, add an ADR
3. Commit with descriptive messages: `feat: implement horoscope caching service`
