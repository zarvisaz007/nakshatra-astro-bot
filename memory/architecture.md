# Architecture

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Bot framework | aiogram 3.x | Async, FSM, middleware support |
| Astrology engine | kerykeion | Pure Python, natal + transit |
| AI | Claude API (claude-haiku-4-5) | Short text, cheap, fast |
| Cache | Redis | TTL = midnight UTC |
| Database | SQLite (dev) / PostgreSQL (prod) | Via SQLAlchemy async |
| ORM | SQLAlchemy 2.x + asyncpg/aiosqlite | Async sessions |
| Config | pydantic-settings | .env parsing, type-safe |
| Deployment | Railway | Git-push, Postgres + Redis plugins |

## Component Map

```
Telegram User
      |
      v
[aiogram Dispatcher]
      |
      +---> [Command Handlers] (/start, /horoscope, /chart, /sign)
                  |
                  +---> [UserService]  <--> [SQLAlchemy] <--> [SQLite/Postgres]
                  |         (birth data, profile CRUD)
                  |
                  +---> [AstrologyService]
                  |         (kerykeion: natal chart, sun sign, aspects)
                  |
                  +---> [HoroscopeService]
                            |
                            +---> [Redis] (cache hit? return cached)
                            |
                            +---> [Claude API] (cache miss: generate + store)
```

## Data Flow: /horoscope command

```
User sends /horoscope
      |
      v
Handler fetches user profile from DB (sun sign)
      |
      v
HoroscopeService.get_reading(sign, date)
      |
      +--[Redis HIT]--> return cached reading
      |
      +--[Redis MISS]--> call Claude API
                              |
                              v
                         Store in Redis (TTL = seconds until midnight UTC)
                              |
                              v
                         Return reading to user
```

## Data Flow: /chart command

```
User sends /chart
      |
      v
Handler fetches user profile (birth date, time, lat/lon)
      |
      v
AstrologyService.get_natal_chart(birth_data)
      |  (kerykeion calculates positions)
      v
Format as readable text message
      |
      v
Send to user (no caching — user-specific)
```

## Database Schema (simplified)

```
users
  id            INTEGER PK
  telegram_id   BIGINT UNIQUE
  birth_date    DATE
  birth_time    TIME (nullable)
  birth_lat     FLOAT
  birth_lon     FLOAT
  city_name     TEXT
  created_at    TIMESTAMP
```

## Redis Key Convention

```
horoscope:{sign}:{YYYY-MM-DD}   -> reading text   TTL: seconds until midnight UTC
```
Example: `horoscope:aries:2026-03-16`
