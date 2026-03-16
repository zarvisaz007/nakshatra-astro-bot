# Roadmap — Nakshatra Astro Bot

## Phase 1 — Foundation MVP ✅ COMPLETE

- [x] Project bootstrap, docs, architecture
- [x] aiogram 3.x bot, Redis FSM, SQLite DB
- [x] Language selector (Hindi / English)
- [x] Onboarding FSM: name → gender → DOB → time → city → AI intro
- [x] Vedic/sidereal (Lahiri) astrology via kerykeion
- [x] Kundli: Lagna, Rashi, Nakshatra (pada+lord), planets, Dasha
- [x] /horoscope — Vedic daily with lucky number + color
- [x] /kundli — full birth chart
- [x] /panchang — Tithi, Nakshatra, Rahu Kaal, Abhijit Muhurat
- [x] /ask — AI Q&A with Kundli context (3 free, paywall prompt)
- [x] /spiritual — daily mantra + planet influence
- [x] /sign — zodiac info
- [x] OpenRouter AI (GLM 4.5 Air free)
- [x] Bot command menu registered

---

## Phase 2 — Monetization Features ✅ COMPLETE

**Note: Payment module SKIPPED.**

- [x] Admin UI — FastAPI web panel on localhost:8080
- [x] /match — Guna Milan compatibility score (0–36)
- [x] /dosha — Manglik, Kaal Sarp, Shani, Pitru dosha detection
- [x] /lucky — Lucky numbers, colors, gemstones, name letters
- [x] /remedy — Mantra, donation, fasting, dasha remedy

---

## Phase 3 — Advanced Astrology ✅ COMPLETE

- [x] /career — 10th house career analysis + AI reading
- [x] /marriage — 7th house marriage prediction + AI reading
- [x] /wealth — 2nd/11th house wealth analysis + AI reading
- [x] /dasha — Vimshottari Dasha timeline (current + next 5 periods)

---

## Phase 4 — Spiritual Services ✅ COMPLETE

- [x] /puja — dasha-based puja + Navagraha/Mangal/Shani Shanti/Kaal Sarp special pujas + AI reading
- [x] /mantra — nakshatra lord beeja mantra + dasha mantra + element-based sadhana tips + AI reading
- [x] /gems — lagna lord primary gem + supporting gems + gems to avoid + AI reading
- [ ] Temple puja booking (skipped — requires partner integration)

---

## Phase 5 — AI Enhanced ✅ COMPLETE

- [x] Palm reading (image upload) — `/palmreading`, vision AI (llama-3.2-11b-vision)
- [x] Dream interpretation — `/dream`, FSM, Vedic symbolism + kundli context
- [x] Numerology AI — `/numerology`, Chaldean + Vedic planets, Redis cached

---

## Phase 6 — Subscriptions

- [ ] Basic ₹199/month
- [ ] Premium ₹499/month
- [ ] Elite ₹999/month
- [ ] Feature gates by tier

---

## Phase 7 — Retention ✅ COMPLETE

- [x] Scheduled daily horoscope push — 7 AM IST daily to opted-in users
- [x] Transit alerts — moon nakshatra change alerts
- [x] Festival/Ekadashi reminders — 1 day before major Hindu festivals
- [x] Weekly digest — Monday 5 AM UTC AI-generated weekly outlook
- [x] `/notifications` — user toggle for notifications (default: on)

---

## Phase 8 — Viral Growth ✅ COMPLETE

- [x] /reportcard — shareable destiny card image (900×500 Pillow, cosmic theme)
- [x] /sharecard — shareable compatibility card image (score bar, guna details)
- [x] /milestones — life milestones + dasha age timeline + AI forecast (7-day cache)
