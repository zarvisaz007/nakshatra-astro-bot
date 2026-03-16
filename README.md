# Nakshatra Astro Bot

AI-powered Vedic astrology Telegram bot for the Indian market.
**[@Nakshatra_Astrobot](https://t.me/Nakshatra_Astrobot)** — Hindi + English

---

## Features — 24 Commands

### Core Astrology
| Command | Description |
|---------|-------------|
| `/start` | Onboarding: language → name → DOB → city → AI intro |
| `/horoscope` | Vedic daily horoscope with lucky number + color |
| `/kundli` | Full birth chart: lagna, rashi, nakshatra, planets, dasha |
| `/panchang` | Today's Tithi, Nakshatra, Rahu Kaal, Abhijit Muhurat |
| `/ask` | AI Q&A with your kundli context (3 free questions) |
| `/spiritual` | Daily mantra + planet influence |
| `/sign` | Zodiac sign info — no account needed |
| `/dasha` | Vimshottari Dasha timeline (current + next 5 periods) |

### Compatibility & Relationships
| Command | Description |
|---------|-------------|
| `/match` | Guna Milan compatibility score (0–36) |
| `/dosha` | Manglik, Kaal Sarp, Shani, Pitru dosha analysis |
| `/marriage` | 7th house marriage prediction + AI reading |

### Life & Finance
| Command | Description |
|---------|-------------|
| `/career` | 10th house career analysis + AI reading |
| `/wealth` | 2nd/11th house wealth analysis + AI reading |
| `/lucky` | Lucky numbers, colors, gemstones, name letters |
| `/remedy` | Personal remedies: mantra, donation, fasting |

### Spiritual Services
| Command | Description |
|---------|-------------|
| `/puja` | Dasha-based puja + Navagraha puja recommendations |
| `/mantra` | Nakshatra beeja mantra + sadhana tips |
| `/gems` | Gemstone recommendations (lagna lord + supporting) |

### AI Enhanced
| Command | Description |
|---------|-------------|
| `/numerology` | Chaldean numerology with Vedic planetary mapping |
| `/dream` | Vedic dream interpretation |
| `/palmreading` | Send palm photo → AI palm line reading |

### Retention & Growth
| Command | Description |
|---------|-------------|
| `/notifications` | Toggle daily push notifications (default: on) |
| `/reportcard` | Shareable destiny card image |
| `/sharecard` | Shareable compatibility card image |
| `/milestones` | Life milestones + dasha age forecast |

---

## Stack

| Layer | Technology |
|---|---|
| Bot framework | aiogram 3.x (async, FSM) |
| Astrology engine | kerykeion (Vedic/sidereal Lahiri) |
| AI text | OpenRouter GLM 4.5 Air (free) |
| AI vision | llama-3.2-11b-vision (free) — palm reading |
| Cache | Redis (prevents redundant AI calls) |
| Database | SQLite dev / PostgreSQL prod |
| ORM | SQLAlchemy 2.x async |
| Images | Pillow (destiny + compatibility cards) |
| Admin UI | FastAPI + Jinja2 (localhost:8080) |
| Scheduler | asyncio background task |

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/zarvisaz007/nakshatra-astro-bot
cd nakshatra-astro-bot

# 2. Create virtualenv + install deps
python3.13 -m venv venv
venv/bin/pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Fill in: TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY

# 4. Start Redis
brew services start redis     # macOS
# or: redis-server &

# 5. Run the bot
venv/bin/python -m app.bot

# 6. (Optional) Admin UI in a second terminal
venv/bin/python -m app.admin  # → http://localhost:8080
```

---

## Environment Variables

```env
TELEGRAM_BOT_TOKEN=        # From @BotFather
OPENROUTER_API_KEY=        # From openrouter.ai
OPENROUTER_MODEL=z-ai/glm-4.5-air:free
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./astro.db
ADMIN_PASSWORD=nakshatra_admin
ADMIN_PORT=8080
```

For production, change `DATABASE_URL` to `postgresql+asyncpg://...` — no code changes needed.

---

## Project Structure

```
app/
├── bot.py              — Entry point: all 24 routers + scheduler
├── config.py           — pydantic-settings (.env)
├── database.py         — Async SQLAlchemy engine + session factory
├── i18n.py             — UI strings (en/hi) for Phases 1–4
├── admin/              — FastAPI admin UI (localhost:8080)
├── models/user.py      — User model (birth data, tier, notifications)
├── services/           — All business logic + AI calls
└── handlers/           — 24 aiogram command handlers
memory/                 — Architecture, decisions, requirements, roadmap
```

---

## Key Design Decisions

- **Vedic only** — always Sidereal/Lahiri, never tropical
- **Cache first** — Redis caching keeps AI costs near-zero at scale (12 signs × 2 langs = 24 calls/day max for /horoscope)
- **Async everywhere** — blocking calls (Pillow, geocoding) run in thread executor
- **Free AI** — OpenRouter free tier handles early growth; upgrade path exists

See `memory/decisions.md` for full ADR log.

---

## What's Next — Phase 6

**Subscriptions** — Razorpay payment integration + feature gates by tier:
- Basic ₹199/month — unlimited `/ask`
- Premium ₹499/month — priority AI + reports
- Elite ₹999/month — personal astrologer chat

The `subscription_tier` column is already in the User model. Just needs payment + gates.

---

## Documentation

See [`memory/`](memory/) for full architecture, decisions, requirements, and roadmap.
