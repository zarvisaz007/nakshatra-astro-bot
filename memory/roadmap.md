# Roadmap

## Phase 1 — MVP

**Goal:** Functional bot with core features, deployed and usable.

**Features:**
- [x] Project bootstrap (repo, docs, structure)
- [x] `app/config.py` — pydantic-settings config
- [x] `app/models/user.py` — SQLAlchemy User model
- [x] `app/services/user.py` — get_or_create, update_birth_data
- [x] `app/services/astrology.py` — kerykeion natal chart + sun sign
- [x] `app/services/horoscope.py` — Claude API reading generation
- [x] `app/services/cache.py` — Redis read/write with TTL
- [x] `app/handlers/start.py` — onboarding FSM (collect birth data)
- [x] `app/handlers/horoscope.py` — `/horoscope` command
- [x] `app/handlers/chart.py` — `/chart` command
- [x] `app/handlers/sign.py` — `/sign` command
- [x] `app/bot.py` — entry point, dispatcher wiring
- [x] `requirements.txt` + `.env.example`
- [ ] Deploy to Railway

**Success criteria:** 10 test users onboarded, horoscopes generating correctly.

---

## Phase 2 — Growth Features

**Goal:** Add engagement features that drive return visits.

**Features:**
- [ ] `/match [sign]` — compatibility reading between two signs (Claude-generated)
- [ ] Daily horoscope push notifications (opt-in, scheduled via APScheduler)
- [ ] Transit alerts — notify user when major planet transits their natal placements
- [ ] Inline mode — `@botname aries` returns sign info in any chat
- [ ] `/delete_account` — GDPR compliance, wipe user data

**Dependencies:** Phase 1 complete + stable user base.

---

## Phase 3 — Premium Tier

**Goal:** Monetization to cover infrastructure costs.

**Features:**
- [ ] Stripe payment integration (Telegram Stars or card)
- [ ] Premium: detailed natal chart PDF export (reportlab or weasyprint)
- [ ] Premium: year-ahead forecast (Claude, monthly breakdown)
- [ ] Premium: personalized daily reading (per-user, not per-sign cache)
- [ ] Multi-language support (i18n via fluent or gettext)
- [ ] Admin dashboard (simple web UI, FastAPI + htmx)

**Dependencies:** Phase 2 complete, >500 active users.

---

## Backlog / Ideas

- Synastry charts (two people's charts overlaid)
- Moon phase tracker
- Retrograde notifications
- Astrocartography (location-based destiny map)
- Integration with Google Calendar for auspicious dates
