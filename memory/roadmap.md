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

## Phase 2 — Monetization Features (IN PROGRESS)

**Note: Payment module SKIPPED. Features built as free/premium-gated stubs.**

### Admin UI (priority)
- [ ] `app/admin/` — FastAPI web panel on localhost:8080
- [ ] Password-protected dashboard
- [ ] Settings page: change API key, model, admin password
- [ ] User stats: total users, active today, questions asked
- [ ] User lookup by Telegram ID
- [ ] Live config reload without bot restart

### Kundli Matching
- [ ] /match command — enter partner's birth details
- [ ] Guna Milan score (out of 36)
- [ ] Manglik check for both
- [ ] AI-generated compatibility reading

### Dosha Detection
- [ ] /dosha command
- [ ] Manglik Dosha
- [ ] Kaal Sarp Dosha
- [ ] Shani Dosha
- [ ] Rahu-Ketu Dosha
- [ ] Pitru Dosha
- [ ] AI explanation + remedy hint

### Lucky Name & Number
- [ ] /lucky command
- [ ] Lucky baby names (numerology-based)
- [ ] Lucky business name
- [ ] Lucky numbers (from Nakshatra lord + DOB)
- [ ] Lucky days/colors

### Personal Remedies
- [ ] /remedy command
- [ ] Mantra recommendation (based on weak planets)
- [ ] Donation suggestion (by day + planet)
- [ ] Fasting recommendation
- [ ] Temple/deity recommendation

---

## Phase 3 — Advanced Astrology (Next)

- [ ] Full Kundli analysis report (career, finance, marriage, health)
- [ ] Planetary Dasha prediction (10-year timeline)
- [ ] Career astrology (/career)
- [ ] Marriage prediction (/marriage)
- [ ] Wealth astrology (/wealth)

---

## Phase 4 — Spiritual Services

- [ ] Puja recommendations (Shani, Navagraha, etc.)
- [ ] Personalized Mantra Sadhana
- [ ] Gemstone recommendation
- [ ] Temple puja booking (partner integration)

---

## Phase 5 — AI Enhanced

- [ ] Palm reading (image upload)
- [ ] Dream interpretation
- [ ] Numerology AI

---

## Phase 6 — Subscriptions

- [ ] Basic ₹199/month
- [ ] Premium ₹499/month
- [ ] Elite ₹999/month
- [ ] Feature gates by tier

---

## Phase 7 — Retention

- [ ] Scheduled daily horoscope push
- [ ] Transit alerts
- [ ] Festival/Ekadashi reminders
- [ ] Weekly digest

---

## Phase 8 — Viral Growth

- [ ] Shareable destiny report card (image)
- [ ] Compatibility test share
- [ ] Age prediction
