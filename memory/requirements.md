# Requirements

## Functional Requirements

### FR-001: User Onboarding
- Bot greets new users with `/start`
- Collects birth date (required), birth time (optional), birth location (required for chart)
- Stores data in database linked to Telegram user ID
- Allows users to update their birth data

### FR-002: Daily Horoscope
- `/horoscope` returns today's reading for the user's sun sign
- Reading is AI-generated (Claude), ~150-250 words
- Reading is cached per sign per day — same sign gets same text
- Gracefully handles users who haven't set birth data (prompt to onboard)

### FR-003: Natal Chart
- `/chart` returns a text summary of the user's natal chart
- Includes: sun, moon, rising sign; major planetary positions; dominant aspects
- Requires birth date + location (time needed for accurate rising sign)
- Calculated via kerykeion, formatted for readability in Telegram

### FR-004: Sign Lookup
- `/sign [zodiac]` returns a brief description of any zodiac sign
- Works without user account or birth data
- Accepts full name (`aries`) or abbreviation (`ari`)

### FR-005: Error Handling
- Graceful messages for invalid inputs
- Rate limiting: max 10 requests/minute per user
- Timeout handling for Claude API calls (max 30s)

---

## Non-Functional Requirements

### NFR-001: Cost
- Claude API cost < $5/month for first 1,000 active users
- Achieved via Redis caching (12 calls/day max)

### NFR-002: Latency
- Cached horoscope response: < 500ms
- Uncached (first of day per sign): < 5s
- Natal chart calculation: < 2s

### NFR-003: Reliability
- Uptime > 99%
- Bot handles Telegram API outages gracefully (retry with backoff)
- Database writes are transactional

### NFR-004: Privacy
- Birth data stored only in operator's database
- No third-party analytics on user data
- Users can delete their data via `/delete_account`

### NFR-005: Scalability
- Architecture supports 10,000+ users without code changes
- Horizontal scaling: stateless bot process + Redis + Postgres

### NFR-006: Maintainability
- All config via environment variables
- Structured logging (JSON) for Railway log drain
- Single `requirements.txt` with pinned versions
