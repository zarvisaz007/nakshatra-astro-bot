# Project Summary — Nakshatra Astro Bot

## What It Is

**Nakshatra Astro** (`@Nakshatra_Astrobot`) is a full-featured AI Vedic astrology Telegram bot for the Indian market.

- 24 commands covering the complete Vedic astrology experience
- Hindi + English bilingual support
- Vedic/sidereal (Lahiri) calculations via kerykeion
- AI readings via OpenRouter GLM 4.5 Air (free tier)
- Shareable image cards for viral growth
- Background scheduler for daily retention pushes

## Goals

- Deliver genuine Vedic astrology value — not canned text
- Keep AI costs minimal via Redis caching (most heavy commands: <50 AI calls/day regardless of users)
- Retain users via daily horoscope push, transit alerts, festival reminders
- Drive viral growth via shareable destiny and compatibility card images
- Monetize via subscription tiers (Phase 6 — not yet built)

## Target Users

- Daily horoscope checkers (Indian, 18–45)
- People planning life decisions (career, marriage, business) using astrology
- Parents looking for baby name numerology / kundli matching
- Spiritually inclined users seeking mantras, pujas, remedies
- Telegram-native users who prefer bots over apps

## Current Feature Set

### Core Astrology
- Full Vedic kundli (lagna, rashi, nakshatra+pada, all planets, dasha)
- Daily horoscope with lucky number + color
- Panchang (Tithi, Rahu Kaal, Abhijit Muhurat)
- Vimshottari Dasha timeline

### Compatibility & Relationships
- Guna Milan (0–36 score, all 8 gunas)
- Dosha detection (Manglik, Kaal Sarp, Shani, Pitru)
- Marriage prediction (7th house + AI)

### Life Areas
- Career analysis (10th house + AI)
- Wealth analysis (2nd/11th house + AI)
- Lucky numbers, colors, gemstones, name letters

### Spiritual Services
- Personal remedies (mantra, donation, fasting)
- Puja recommendations (dasha-based + Navagraha)
- Nakshatra beeja mantra + sadhana
- Gemstone recommendations (lagna lord + supporting)

### AI Enhanced (Phase 5)
- Chaldean numerology with Vedic planetary mapping
- Vedic dream interpretation
- Palm reading via photo upload (vision AI)

### Retention (Phase 7)
- Daily horoscope push at 7 AM IST to opted-in users
- Moon nakshatra transit alerts
- Festival + Ekadashi reminders
- Weekly astrology digest every Monday

### Viral Growth (Phase 8)
- Shareable destiny report card (900×500 image)
- Shareable compatibility card image
- Life milestones + dasha age forecast

## What's NOT Built Yet

- **Phase 6: Subscriptions** — ₹199/₹499/₹999 tiers, Razorpay payment, feature gates
- Temple puja booking (requires partner integration)
- PDF report generation
- Web interface

## Success Metrics (targets)

- User retention: >30% return after day 1 (daily push helps)
- Viral coefficient: >0.3 (shareable cards)
- AI cost: <₹500/month for first 10,000 users (heavy Redis caching)
- Uptime: >99%

## Revenue Model (when Phase 6 is built)

| Tier | Price | Features |
|------|-------|---------|
| Free | ₹0 | All commands, 3 /ask questions |
| Basic | ₹199/mo | Unlimited /ask |
| Premium | ₹499/mo | All Basic + priority AI |
| Elite | ₹999/mo | All Premium + personal astrologer chat |
