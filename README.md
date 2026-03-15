# Astrology Telegram Bot

A Telegram bot that delivers personalized daily horoscopes and natal chart readings powered by Claude AI and kerykeion astrology engine.

## Features

- `/start` — Onboarding: collect birth date, time, and location
- `/horoscope` — Today's AI-generated reading for your sun sign (Redis-cached)
- `/chart` — Your natal chart summary (planetary positions + aspects)
- `/sign [zodiac]` — Quick sign lookup, no account required

## Stack

| Layer | Technology |
|---|---|
| Bot framework | aiogram 3.x |
| Astrology engine | kerykeion |
| AI readings | Claude API (claude-haiku-4-5) |
| Cache | Redis (12 calls/day max) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy (async) |
| Deployment | Railway |

## Quickstart

```bash
# 1. Clone and enter project
git clone <repo> && cd claude-terminal

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and fill in environment variables
cp .env.example .env

# 5. Run the bot
python -m app.bot
```

## Environment Variables

```
TELEGRAM_BOT_TOKEN=        # BotFather token
ANTHROPIC_API_KEY=         # Anthropic API key
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./astro.db   # dev
# DATABASE_URL=postgresql+asyncpg://...       # prod
```

## Project Structure

```
claude-terminal/
├── app/
│   ├── bot.py             # Entry point, dispatcher setup
│   ├── handlers/          # Telegram command handlers
│   ├── services/          # Astrology, Claude, cache logic
│   ├── models/            # SQLAlchemy ORM models
│   └── config.py          # Settings via pydantic-settings
├── memory/                # Project documentation
├── requirements.txt
├── .env.example
└── README.md
```

## Deployment (Railway)

1. Push repo to GitHub
2. Connect repo in Railway dashboard
3. Add environment variables
4. Add Redis and PostgreSQL plugins
5. Deploy — Railway auto-detects Python via `requirements.txt`

## Memory / Docs

See [`memory/`](memory/) for architecture, decisions, requirements, and roadmap.
