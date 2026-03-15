# Project Summary

## What It Does

An astrology Telegram bot that:
1. Collects the user's birth data (date, time, location) on first use
2. Generates a personalized daily horoscope using Claude AI
3. Calculates and presents the user's natal chart (planetary positions + aspects)
4. Supports quick sign lookups without requiring an account

## Goals

- Deliver genuinely useful, AI-quality horoscope readings (not canned text)
- Keep Claude API costs minimal via Redis caching (12 calls/day max regardless of user count)
- Run cheaply at scale — Railway free tier viable for early growth
- Be privacy-conscious: birth data stored locally, never sold

## Scope

**In scope (MVP):**
- Telegram bot interface only
- Daily sun-sign horoscope (cached per sign, not per user)
- Natal chart text summary
- User profile with birth data storage

**Out of scope (for now):**
- Web interface
- Push notifications / proactive alerts
- Payment processing
- PDF exports

## Target Users

- Astrology enthusiasts who check their horoscope daily
- Curious users who want to understand their natal chart
- Telegram-native users who prefer bots to apps

## Success Metrics

- User retention: >30% return after day 1
- Cost: <$5/month in Claude API costs for first 1,000 users
- Uptime: >99% (Railway SLA)
