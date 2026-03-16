# Requirements — Nakshatra Astro Bot

## Functional Requirements

### FR-001: Onboarding (Phase 1)
- `/start` FSM: language → name → gender (optional) → DOB → birth time (optional) → birth city
- Geocode city to lat/lon/timezone via geopy + timezonefinder
- AI-generated personalized intro on completion
- Welcome back message if already onboarded

### FR-002: Core Astrology (Phase 1)
- `/horoscope` — Vedic daily horoscope, lucky number + color, cached per sign+lang until midnight
- `/kundli` — full birth chart: lagna, rashi, nakshatra+pada+lord, all planets, current dasha
- `/panchang` — Tithi, Nakshatra+lord, Sun/Moon sign, Rahu Kaal, Abhijit Muhurat
- `/ask` — AI Q&A with kundli context, 3 free for `free` tier
- `/spiritual` — daily mantra + planet influence, cached per moon sign
- `/sign [zodiac]` — sign info, no account needed

### FR-003: Matching & Doshas (Phase 2)
- `/match` — FSM: collect partner name + DOB + city → Guna Milan 0–36 + Manglik check
- `/dosha` — Manglik, Kaal Sarp, Shani, Pitru dosha detection with remedies
- `/lucky` — lucky numbers, colors, gemstones, favorable name letters
- `/remedy` — personalized remedies (mantra, donation, fasting) based on dasha + doshas
- Admin UI at localhost:8080 — FastAPI, password-protected, view user stats

### FR-004: Advanced Astrology (Phase 3)
- `/career` — 10th house analysis + career domains + AI reading, cached
- `/marriage` — 7th house + Venus/Jupiter + AI reading, cached
- `/wealth` — 2nd/11th house + AI reading, cached
- `/dasha` — Vimshottari timeline: current + next 5 periods with dates and themes

### FR-005: Spiritual Services (Phase 4)
- `/puja` — dasha-based + Navagraha/Mangal/Shani Shanti/Kaal Sarp puja AI reading
- `/mantra` — nakshatra beeja mantra + dasha mantra + element sadhana tips + AI
- `/gems` — lagna lord primary gem (metal, finger, weight, caution) + supporting + avoid

### FR-006: AI Enhanced (Phase 5)
- `/numerology` — Chaldean numerology: Life Path, Destiny, Soul Urge, Day, Personal Year
  - Vedic planetary mapping (1=Sun, 2=Moon, ... 9=Mars)
  - AI reading, cached until midnight
- `/dream` — FSM: user describes dream → Vedic symbolism AI interpretation with kundli context
- `/palmreading` — FSM: user sends palm photo → vision AI reads life/head/heart/fate lines
  - Uses `meta-llama/llama-3.2-11b-vision-instruct:free` model
  - Vedic context (lagna, nakshatra, dasha) included in prompt

### FR-007: Retention (Phase 7)
- `/notifications` — inline keyboard toggle, default on, stored in `notifications_enabled` DB column
- **Daily horoscope push** — 01:30 UTC (7 AM IST) to all opted-in users
- **Transit alerts** — sent when moon nakshatra changes (detected every 30 min)
- **Festival reminders** — sent at 06:00 UTC the day before major Hindu festivals + Ekadashi
- **Weekly digest** — Monday 05:00 UTC, AI-generated weekly planetary outlook

### FR-008: Viral Growth (Phase 8)
- `/reportcard` — generates 900×500 Pillow PNG: name, DOB, lagna, rashi, nakshatra, dasha,
  numerology life path + planet, destiny number, lucky no+color swatch — shareable
- `/sharecard` — FSM: partner name + DOB → compatibility card image with score bar + gunas — shareable
- `/milestones` — Vimshottari dasha age-range timeline + AI life milestone forecast
  - Career peak, marriage window, wealth period, spiritual phase age ranges
  - Cached 7 days per user

---

## Non-Functional Requirements

### NFR-001: Cost
- AI cost < ₹500/month for first 10,000 active users
- Achieved via Redis caching (most commands: <50 AI calls/day regardless of user count)
- Uncached commands (/ask, /dream, /palmreading): rate-limited via `free_questions_used`

### NFR-002: Latency
- Cached response: < 500ms
- Uncached AI response: < 8s (GLM thinking model is slower)
- Image generation (/reportcard, /sharecard): < 3s (Pillow in thread executor)

### NFR-003: Reliability
- Bot handles Telegram API outages (aiogram retry backoff)
- Scheduler catches all exceptions per user — one failure doesn't stop others
- DB writes transactional via SQLAlchemy sessions

### NFR-004: Language
- All 24 commands support Hindi + English
- Phases 1–4: strings in `app/i18n.py` via `t(lang, key)`
- Phases 5–8: inline `_STRINGS` dicts per handler

### NFR-005: Vedic Accuracy
- ALWAYS use `zodiac_type="Sidereal"`, `sidereal_mode="LAHIRI"` — no exceptions
- Nakshatra lookup: 27 nakshatras with Chandra (Moon) absolute position
- Dasha: Vimshottari system, 9 planets, 120-year cycle

### NFR-006: Scalability
- Architecture supports 10,000+ users without code changes
- Switch to Postgres: change `DATABASE_URL` only
- Scheduler handles growing user lists (per-user exception catching)

### NFR-007: Privacy
- Birth data stored only in operator's DB
- No third-party analytics on user data
- Users can opt out of notifications via /notifications

---

## Constraints

- **No payment module** — skip until explicitly asked (Phase 6)
- **No temple booking** — requires partner integration, skip
- **No PDF export** — not requested yet
- **No web interface** — Telegram only
- **GLM max_tokens=800** — hard requirement, never lower
