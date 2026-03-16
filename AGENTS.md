# AGENTS.md — Multi-Agent Collaboration Guide

> For AI agents (Claude Code, Codex, Cursor, Copilot, etc.) working on this project.
> **Read CLAUDE.md first** — it has the full onboarding, file structure, and rules.

## Project State

**Nakshatra Astro** — Phases 1–5, 7, 8 complete. 24 commands live.
**Phase 6 (Subscriptions)** is the only remaining phase.

All code is implemented and running. Do NOT rewrite existing features. Read before touching.

---

## Repository Layout

```
claude-terminal/
├── CLAUDE.md          ← FULL agent onboarding — READ THIS FIRST
├── AGENTS.md          ← This file (multi-agent guide)
├── MEMORY.md          ← Index of memory/ docs
├── README.md          ← Human-facing overview
├── requirements.txt   ← All pinned deps including Pillow
├── .env               ← Secrets (not in git)
├── app/               ← All bot code (see CLAUDE.md for full tree)
├── memory/
│   ├── project_summary.md   ← Goals, scope, users, revenue model
│   ├── architecture.md      ← Stack, component map, DB schema, Redis keys
│   ├── decisions.md         ← ADRs 001–010 (why each tech was chosen)
│   ├── requirements.md      ← All functional + non-functional requirements
│   └── roadmap.md           ← Phase checklist (Phases 1–8)
└── venv/              ← Python virtualenv (do not commit)
```

---

## Rules for Agents

### Critical
1. **Vedic only** — `zodiac_type="Sidereal"`, `sidereal_mode="LAHIRI"` always
2. **Async everywhere** — no blocking calls in handlers; Pillow → `run_in_executor`
3. **Cache before AI** — check Redis before every OpenRouter call
4. **Thin handlers** — logic lives in `services/`, handlers orchestrate only
5. **GLM max_tokens=800** — never lower; it's a thinking model
6. **Delete astro.db when adding columns** — no migration tooling

### Style
- New handlers: follow pattern in `app/handlers/gems.py` (Phase 4 reference)
- New AI services: follow pattern in `app/services/horoscope.py` (_call_ai reuse)
- New image features: follow pattern in `app/services/card_service.py`
- Phases 5–8 strings: inline `_STRINGS = {"en": {...}, "hi": {...}}` dict per handler
- No payment code until explicitly asked

---

## How Handlers Are Wired

Every handler needs 3 things in `app/bot.py`:
```python
# 1. Import
from app.handlers import my_handler

# 2. Register router
dp.include_router(my_handler.router)

# 3. Add bot command
BotCommand(command="mycommand", description="..."),
```

---

## Phase 6 — What Needs to Be Built

**Subscriptions** (not yet started):

```
app/
├── handlers/
│   └── subscription.py     — /subscribe command, tier selection
├── services/
│   └── payment_service.py  — Razorpay webhook handling, tier upgrade
```

User model already has `subscription_tier` column (`free/basic/premium/elite`).
`/ask` already checks `subscription_tier` for unlimited questions.

Steps:
1. Razorpay integration (or Stripe for international)
2. `/subscribe` command with inline keyboard (Basic / Premium / Elite)
3. Payment webhook → update `subscription_tier` in DB
4. Feature gates: `/ask` unlimited for non-free, `/dream` limited for free, etc.

---

## After Completing Work

1. Check off items in `memory/roadmap.md`
2. Add ADR to `memory/decisions.md` if a new tech choice was made
3. Update `CLAUDE.md` "Current State" section if a new phase is completed
4. Commit: `feat:` / `fix:` / `chore:` prefix
5. Push: `git push origin main`
6. Restart bot: `pkill -f app.bot && rm astro.db && venv/bin/python -m app.bot &`
