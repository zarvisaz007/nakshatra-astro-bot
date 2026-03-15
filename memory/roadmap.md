# Roadmap — Nakshatra Astro Bot

## Phase 1 — Foundation MVP ✅ (partially done)

**Goal:** Working bot with Vedic astrology core, daily engagement, AI consultation.

### Infrastructure ✅
- [x] Project bootstrap, docs, architecture
- [x] aiogram 3.x bot, Redis FSM, SQLite DB
- [x] Language selector (Hindi / English)
- [x] Flexible onboarding (date/time/location)
- [x] Western horoscope via kerykeion
- [x] OpenRouter AI (GLM 4.5 Air free)

### Phase 1 — Remaining (in progress)
- [ ] Add name + gender to user profile
- [ ] Switch to Vedic (sidereal/Lahiri) calculations
- [ ] Kundli summary: Lagna, Rashi, Nakshatra, planet placements
- [ ] AI-generated personalized introduction on onboarding
- [ ] Enhanced daily horoscope: lucky number, color, time, advice
- [ ] Daily Panchang: Tithi, Nakshatra, Rahu Kaal, Abhijit Muhurat
- [ ] Daily Spiritual Guidance: planet influence + mantra
- [ ] Ask AI (/ask command): 3 free questions, then paywall
- [ ] Question counter in DB

---

## Phase 2 — Monetization Features

**Goal:** Paid services replicating what people pay Pandits for.

**Price range:** ₹49–₹299

- [ ] Payment integration (Razorpay or Telegram Stars)
- [ ] Detailed Horoscope Report (personality, strengths, challenges)
- [ ] Kundli Matching (Guna Milan, Manglik, compatibility score)
- [ ] Dosha Detection (Manglik, Kaal Sarp, Shani, Rahu-Ketu, Pitru)
- [ ] Lucky Name & Number (baby names, business name, vehicle, mobile)
- [ ] Personal Remedies (mantra, donation, fasting, temple)

---

## Phase 3 — Advanced Astrology Services

**Goal:** Deep insights matching professional astrologers.

**Price range:** ₹499–₹1999

- [ ] Full Kundli Analysis (career, finance, marriage, health, travel)
- [ ] Planetary Dasha Prediction (Mahadasha, 10-year timeline)
- [ ] Career Astrology (best fields, promotion timing, job change)
- [ ] Marriage Prediction (timing, love vs arranged, spouse personality)
- [ ] Wealth Astrology (wealth cycles, investment timing, risks)

---

## Phase 4 — Spiritual Remedies & Puja Services

**Goal:** Monetize like traditional Pandits.

**Price range:** ₹2000–₹10,000+

- [ ] Personalized Puja Recommendations (Shani, Navagraha, Rahu-Ketu, etc.)
- [ ] Personalized Mantra Sadhana (exact mantra, count, timing, duration)
- [ ] Gemstone Recommendation (with upsell to purchase)
- [ ] Temple Puja Service (partner temples, photos/videos delivery)

---

## Phase 5 — AI Enhanced Features

**Goal:** Differentiate from normal astrology bots.

- [ ] AI Astrology Chat (birth chart + transit aware)
- [ ] Palm Reading (image upload → AI prediction)
- [ ] Dream Interpretation (write dream → spiritual meaning)
- [ ] Numerology AI (name + DOB → life path, destiny)

---

## Phase 6 — Subscription Model

**Goal:** Recurring revenue.

| Plan | Price | Includes |
|---|---|---|
| Basic | ₹199/month | Unlimited horoscope, AI questions, Panchang, Remedies |
| Premium | ₹499/month | + Detailed predictions, marriage, career, numerology |
| Elite | ₹999/month | + Unlimited AI, full Kundli, puja, priority support |

- [ ] Subscription tier tracking in DB
- [ ] Feature gates by tier
- [ ] Payment + renewal flow

---

## Phase 7 — Retention Features

**Goal:** Daily habit formation.

- [ ] Scheduled daily horoscope push (opt-in)
- [ ] Daily mantra push
- [ ] Planet transit alerts
- [ ] Festival / Ekadashi / Purnima reminders
- [ ] Weekly prediction digest

---

## Phase 8 — Viral Growth Features

**Goal:** Organic sharing.

- [ ] Shareable Destiny Report (image card)
- [ ] Compatibility Test (share with partner)
- [ ] Age Prediction ("what happens at age 30?")
- [ ] Friend Comparison

---

## Success Metrics

- Daily active users
- Questions asked per user
- Paid conversion rate
- Subscription rate
- Day-7 retention
- Day-30 retention
