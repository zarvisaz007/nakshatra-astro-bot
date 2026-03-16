# Architecture — Nakshatra Astro Bot

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Bot framework | aiogram 3.x | Async, FSM, middleware support |
| Astrology engine | kerykeion 4.x | Vedic/sidereal Lahiri, natal charts, transits |
| AI text | OpenRouter GLM 4.5 Air (free) | Via openai SDK, max_tokens=800 |
| AI vision | llama-3.2-11b-vision:free | For /palmreading image analysis |
| Cache | Redis | Key TTLs documented below |
| Database | SQLite (dev) / PostgreSQL (prod) | Via SQLAlchemy 2.x async |
| ORM | SQLAlchemy 2.x + asyncpg/aiosqlite | Async sessions |
| Config | pydantic-settings | .env parsing, type-safe |
| Images | Pillow | Report card + compatibility card generation |
| Scheduler | asyncio background task | run_scheduler() in services/scheduler.py |
| Admin UI | FastAPI + Jinja2 | localhost:8080, basic auth |

---

## Full Component Map

```
Telegram User
      |
      v
[aiogram Dispatcher] ← RedisStorage (FSM state)
      |
      +── [24 Command Handlers] (/start, /horoscope, /kundli, ...)
                |
                +── [UserService]       ←→ [SQLAlchemy] ←→ [SQLite/Postgres]
                |      get_or_create, update_birth_data, increment_questions
                |
                +── [AstrologyService]
                |      get_kundli(), get_nakshatra(), get_panchang()
                |      Vedic sidereal (Lahiri) via kerykeion
                |
                +── [HoroscopeService / AI Services]
                |      _call_ai() → OpenRouter GLM 4.5 Air
                |      Prompts for: horoscope, career, marriage, wealth,
                |                   spiritual, puja, mantra, gems, intro,
                |                   numerology, dream, milestones, weekly
                |
                +── [Redis Cache]
                |      Check before every AI call
                |      Keys: horoscope:*, career:*, numerology:*, milestones:*, sched:*
                |
                +── [VedicService]
                |      guna_milan(), detect_doshas()
                |
                +── [CardService]
                |      generate_report_card()       → Pillow 900×500 PNG
                |      generate_compatibility_card() → Pillow 900×500 PNG
                |
                +── [MilestonesService]
                       get_milestones_data(), get_milestones_reading()

[Scheduler Background Task] ←→ [Bot instance] ←→ [All opted-in users]
      Runs every 30 min:
      - daily horoscope push (01:30 UTC)
      - moon transit alerts
      - festival reminders
      - weekly digest (Mon 05:00 UTC)
```

---

## Database Schema

```sql
users
  id                  INTEGER  PRIMARY KEY
  telegram_id         BIGINT   UNIQUE INDEX
  language            VARCHAR(5)   DEFAULT 'en'       -- 'en' or 'hi'
  name                VARCHAR(100) NULLABLE
  gender              VARCHAR(10)  NULLABLE            -- male/female/other
  birth_date          DATE         NULLABLE
  birth_time          TIME         NULLABLE
  birth_lat           FLOAT        NULLABLE
  birth_lon           FLOAT        NULLABLE
  city_name           VARCHAR(200) NULLABLE
  timezone            VARCHAR(50)  NULLABLE
  free_questions_used INTEGER      DEFAULT 0
  subscription_tier   VARCHAR(20)  DEFAULT 'free'     -- free/basic/premium/elite
  notifications_enabled BOOLEAN    DEFAULT true
  created_at          DATETIME     DEFAULT now()
```

**Note:** Delete `astro.db` whenever adding new columns — no migration tooling.

---

## Redis Key Convention

All keys + their TTLs:

```
# Horoscope cache (shared across users with same sign)
horoscope:{sign_lower}:{YYYY-MM-DD}         TTL: seconds until midnight UTC

# Per-lagna AI caches (shared across users with same lagna+dasha)
career:{lagna}:{dasha}:{lang}               TTL: seconds until midnight UTC
marriage:{lagna}:{dasha}:{lang}             TTL: seconds until midnight UTC
wealth:{lagna}:{dasha}:{lang}               TTL: seconds until midnight UTC
spiritual:{moon_sign}:{lang}                TTL: seconds until midnight UTC

# Per-user / long-lived
numerology:{name_lower}:{dob}:{lang}        TTL: seconds until midnight UTC
milestones:{telegram_id}:{lang}             TTL: 604800s (7 days)

# FSM state (aiogram managed)
fsm:{bot_id}:{chat_id}:{user_id}:state      TTL: managed by aiogram

# Scheduler dedup (prevent double-sends)
sched:sent:daily_horo:{user_id}:{date}      TTL: 86400s (1 day)
sched:transit:moon_nak                      No TTL (persists until changed)
sched:sent:festival:{name}:{year}           TTL: 90 days
sched:sent:weekly:{year}:week{N}            TTL: 14 days
```

---

## Data Flow: /horoscope

```
User sends /horoscope
      ↓
Handler: get user from DB (sun sign, rashi, nakshatra, lang)
      ↓
horoscope.get_reading(sign, rashi, moon_sign, nakshatra, date, lang)
      ↓
  Redis HIT? ──yes──> return cached reading
      │ no
      ↓
  Call OpenRouter GLM (_call_ai prompt)
      ↓
  Store in Redis (TTL = seconds until midnight UTC)
      ↓
  Return reading → format → send to user
```

## Data Flow: /reportcard (image generation)

```
User sends /reportcard
      ↓
Handler: get user + kundli + numerology profile + lucky data
      ↓
generate_report_card(...) — async wrapper
      ↓
loop.run_in_executor(None, _draw_report_card, ...)  — sync Pillow in thread
      ↓
Returns PNG bytes
      ↓
message.answer_photo(BufferedInputFile(bytes, "destiny_card.png"))
```

## Data Flow: Scheduler

```
asyncio.create_task(run_scheduler(bot))  — started in bot.py main()
      ↓
while True:
  _check_daily_horoscope(bot, now)   — 01:30 UTC: push horo to all opted-in users
  _check_transit_alert(bot, now)     — compare current moon nak vs stored
  _check_festivals(bot, now)         — 06:00 UTC: check tomorrow's festivals
  _check_weekly_digest(bot, now)     — Mon 05:00 UTC: AI weekly outlook
  asyncio.sleep(1800)                — check every 30 minutes
```

---

## AI Prompt Architecture

All AI prompts live in `app/services/horoscope.py` as module-level dicts:
```python
_HORO_PROMPT = {"en": "...", "hi": "..."}
_CAREER_PROMPT = {"en": "...", "hi": "..."}
# etc.
```

Single `_call_ai(prompt: str) -> str` function handles all OpenRouter calls.
Vision calls (palm reading) use a separate client in `palm_service.py` with the vision model.

---

## Scalability Notes

**Current bottleneck:** `/ask`, `/dream`, `/palmreading` are not cached — 1 AI call per use.
**Free tier limit:** OpenRouter ~20 req/min. Fine for early growth (<500 users).
**At scale:** Add per-user daily rate limits + asyncio queue for AI calls.
**DB:** Switch `DATABASE_URL` to Postgres in `.env` — zero code changes needed.
