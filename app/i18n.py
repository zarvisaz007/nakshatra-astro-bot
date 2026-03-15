T = {
    "en": {
        # Language selector
        "choose_lang": "🌟 Welcome to *Nakshatra Astro*!\n\nChoose your language:",
        "lang_set": "Language set to English.",
        # Onboarding
        "ask_name": "Namaste! 🙏 What's your *name*?",
        "ask_gender": "Hi {name}! 😊\n\nOptional — what's your *gender*?\n_(helps with Vedic interpretations)_",
        "ask_dob": (
            "What's your *date of birth*?\n\n"
            "Any format works:\n• 24/01/1990\n• 24 Jan 1990\n• January 24, 1990"
        ),
        "ask_tob": (
            "What *time* were you born? (HH:MM, 24h)\n"
            "Example: 14:30\n\nDon't know? Tap *Skip* — rising sign won't be exact."
        ),
        "ask_city": "Which *city* were you born in?",
        "bad_date": "Couldn't read that date. Try: *24 Jan 1990* or *24/01/1990*",
        "bad_time": "Use HH:MM format (e.g. 14:30) or tap *Skip*.",
        "bad_city": "Couldn't find *{city}*. Try a larger nearby city.",
        "welcome_back": "Welcome back, {name}! ✨\n\nTry /horoscope, /kundli, /panchang, or /ask",
        "generating_profile": "✨ Generating your Vedic profile...",
        "onboard_done": (
            "🙏 *Jai Shri Ram, {name}!*\n\n"
            "Your Kundli is ready.\n\n"
            "🌅 *Lagna:* {lagna}\n"
            "🌙 *Rashi:* {rashi}\n"
            "⭐ *Nakshatra:* {nakshatra} (Pada {pada})\n"
            "📅 *Mahadasha:* {dasha}\n\n"
            "_{intro}_\n\n"
            "Try: /horoscope /kundli /panchang /ask"
        ),
        # Commands
        "generating": "🔮 Consulting the stars...",
        "no_profile": "Profile not set up yet. Run /start first!",
        "horo_error": "Couldn't generate horoscope right now. Try again shortly.",
        "chart_error": "Couldn't calculate Kundli. Try again shortly.",
        "ai_error": "Couldn't get a response. Try again shortly.",
        # /horoscope
        "horo_header": "{symbol} *{sign} ({rashi}) — {date}*\n\n",
        "horo_footer": "\n\n🔢 Lucky Number: *{num}*  |  🎨 Lucky Color: *{color}*",
        # /kundli already formatted in astrology.py
        # /panchang
        "panchang_header": "📅 *Panchang — {date}*\n\n",
        "panchang_body": (
            "🌙 *Tithi:* {tithi}\n"
            "⭐ *Nakshatra:* {nakshatra} (Lord: {lord})\n"
            "☀️ *Sun in:* {sun_sign}\n"
            "🌙 *Moon in:* {moon_sign}\n\n"
            "⚠️ *Rahu Kaal:* {rahu_kaal}\n"
            "✨ *Abhijit Muhurat:* {abhijit}\n\n"
            "_Avoid starting new work during Rahu Kaal._"
        ),
        # /ask
        "ask_prompt": "🔮 Ask your astrology question:\n_(3 free questions. {remaining} remaining)_",
        "ask_wait": "🧘 Consulting your Kundli...",
        "ask_limit": (
            "You've used all 3 free questions. 🙏\n\n"
            "To ask more, upgrade to a paid plan:\n"
            "• Basic ₹199/month — unlimited questions\n\n"
            "_(Payment coming soon!)_"
        ),
        # /spiritual
        "spiritual_header": "🕉️ *Daily Spiritual Guidance — {date}*\n\n",
        # Skip button
        "skip": "Skip",
        "male": "Male ♂", "female": "Female ♀", "skip_gender": "Prefer not to say",
    },
    "hi": {
        # Language selector
        "choose_lang": "🌟 *नक्षत्र ज्योतिष* में आपका स्वागत है!\n\nभाषा चुनें:",
        "lang_set": "भाषा हिंदी में सेट की गई।",
        # Onboarding
        "ask_name": "नमस्ते! 🙏 आपका *नाम* क्या है?",
        "ask_gender": "{name} जी! 😊\n\nवैकल्पिक — आपका *लिंग* क्या है?\n_(वैदिक विश्लेषण में सहायक)_",
        "ask_dob": (
            "आपकी *जन्म तिथि* क्या है?\n\n"
            "किसी भी प्रारूप में लिखें:\n• 24/01/1990\n• 24 जन 1990\n• 24 Jan 1990"
        ),
        "ask_tob": (
            "आप किस *समय* पैदा हुए? (HH:MM, 24 घंटे)\n"
            "उदाहरण: 14:30\n\nपता नहीं? *छोड़ें* दबाएं।"
        ),
        "ask_city": "आप किस *शहर* में पैदा हुए?",
        "bad_date": "तिथि समझ नहीं आई। इस तरह लिखें: *24 Jan 1990* या *24/01/1990*",
        "bad_time": "HH:MM प्रारूप (जैसे 14:30) उपयोग करें या *छोड़ें* दबाएं।",
        "bad_city": "*{city}* नहीं मिला। कोई नज़दीकी बड़ा शहर आज़माएं।",
        "welcome_back": "वापसी पर स्वागत है, {name}! ✨\n\n/horoscope, /kundli, /panchang, या /ask आज़माएं",
        "generating_profile": "✨ आपकी वैदिक कुंडली बन रही है...",
        "onboard_done": (
            "🙏 *जय श्री राम, {name}!*\n\n"
            "आपकी कुंडली तैयार है।\n\n"
            "🌅 *लग्न:* {lagna}\n"
            "🌙 *राशि:* {rashi}\n"
            "⭐ *नक्षत्र:* {nakshatra} (पाद {pada})\n"
            "📅 *महादशा:* {dasha}\n\n"
            "_{intro}_\n\n"
            "आज़माएं: /horoscope /kundli /panchang /ask"
        ),
        # Commands
        "generating": "🔮 सितारों से पूछ रहे हैं...",
        "no_profile": "प्रोफ़ाइल अभी सेट नहीं है। पहले /start चलाएं!",
        "horo_error": "अभी राशिफल नहीं बना सके। थोड़ी देर बाद आज़माएं।",
        "chart_error": "कुंडली नहीं बन सकी। थोड़ी देर बाद आज़माएं।",
        "ai_error": "अभी उत्तर नहीं मिला। थोड़ी देर बाद आज़माएं।",
        # /horoscope
        "horo_header": "{symbol} *{sign} ({rashi}) — {date}*\n\n",
        "horo_footer": "\n\n🔢 शुभ अंक: *{num}*  |  🎨 शुभ रंग: *{color}*",
        # /panchang
        "panchang_header": "📅 *पंचांग — {date}*\n\n",
        "panchang_body": (
            "🌙 *तिथि:* {tithi}\n"
            "⭐ *नक्षत्र:* {nakshatra} (स्वामी: {lord})\n"
            "☀️ *सूर्य राशि:* {sun_sign}\n"
            "🌙 *चंद्र राशि:* {moon_sign}\n\n"
            "⚠️ *राहु काल:* {rahu_kaal}\n"
            "✨ *अभिजित मुहूर्त:* {abhijit}\n\n"
            "_राहु काल में नया काम शुरू न करें।_"
        ),
        # /ask
        "ask_prompt": "🔮 अपना ज्योतिष प्रश्न पूछें:\n_(3 मुफ़्त प्रश्न। {remaining} शेष)_",
        "ask_wait": "🧘 आपकी कुंडली देख रहे हैं...",
        "ask_limit": (
            "आपके सभी 3 मुफ़्त प्रश्न खत्म हो गए। 🙏\n\n"
            "और प्रश्न पूछने के लिए:\n"
            "• Basic ₹199/महीना — असीमित प्रश्न\n\n"
            "_(भुगतान जल्द आ रहा है!)_"
        ),
        # /spiritual
        "spiritual_header": "🕉️ *दैनिक आध्यात्मिक मार्गदर्शन — {date}*\n\n",
        # Buttons
        "skip": "छोड़ें",
        "male": "पुरुष ♂", "female": "महिला ♀", "skip_gender": "बताना नहीं",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = T.get(lang, T["en"]).get(key, T["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text
