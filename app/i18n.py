T = {
    "en": {
        "choose_lang": "🌟 Welcome! Choose your language:",
        "lang_set": "Language set to English.",
        "welcome_new": (
            "Welcome to *Nakshatra Astrology* ✨\n\n"
            "I'll need your birth details to get started.\n\n"
            "What's your *birth date*?\n"
            "You can type it any way — examples:\n"
            "• 24/01/1990\n• 24 Jan 1990\n• January 24, 1990"
        ),
        "welcome_back": "Welcome back! ✨ Try /horoscope or /chart.",
        "got_date": "Got it — born *{date}* ✓\n\nWhat time were you born? (HH:MM, 24h)\nExample: 14:30\n\nDon't know? Tap *Skip* — rising sign won't be accurate.",
        "bad_date": "Couldn't read that date. Try: *24 Jan 1990* or *24/01/1990*",
        "got_time": "Time noted ✓\n\nLastly — what *city* were you born in?",
        "skip_time": "No birth time — noted ✓\n\nLastly — what *city* were you born in?",
        "bad_time": "Couldn't parse that. Use HH:MM (e.g. 14:30) or tap *Skip*.",
        "bad_city": "Couldn't find *{city}*. Try a larger nearby city.",
        "onboard_done": (
            "All set! 🎉\n\n"
            "📅 {date}{time}\n"
            "📍 {city}\n\n"
            "Try /horoscope or /chart"
        ),
        "no_profile": "You haven't set up your profile yet. Run /start first!",
        "generating": "Consulting the stars… ✨",
        "horo_error": "Couldn't generate your horoscope right now. Try again shortly.",
        "chart_error": "Couldn't calculate your chart. Try again shortly.",
        "sign_usage": "Usage: /sign <zodiac>\nExample: /sign Aries\n\n{list}",
        "sign_unknown": "Unknown sign *{sign}*. Try /sign for the full list.",
        "skip": "Skip",
    },
    "hi": {
        "choose_lang": "🌟 स्वागत है! अपनी भाषा चुनें:",
        "lang_set": "भाषा हिंदी में सेट की गई।",
        "welcome_new": (
            "*नक्षत्र ज्योतिष* में आपका स्वागत है ✨\n\n"
            "शुरू करने के लिए मुझे आपकी जन्म जानकारी चाहिए।\n\n"
            "आपकी *जन्म तिथि* क्या है?\n"
            "किसी भी तरह लिखें — उदाहरण:\n"
            "• 24/01/1990\n• 24 जन 1990\n• 24 Jan 1990"
        ),
        "welcome_back": "वापसी पर स्वागत है! ✨ /horoscope या /chart आज़माएं।",
        "got_date": "ठीक है — जन्म *{date}* ✓\n\nआप किस समय पैदा हुए? (HH:MM, 24 घंटे)\nउदाहरण: 14:30\n\nपता नहीं? *छोड़ें* दबाएं।",
        "bad_date": "तिथि समझ नहीं आई। इस तरह लिखें: *24 Jan 1990* या *24/01/1990*",
        "got_time": "समय नोट किया ✓\n\nआखिरी सवाल — आप किस *शहर* में पैदा हुए?",
        "skip_time": "जन्म समय नहीं — ठीक है ✓\n\nआखिरी सवाल — आप किस *शहर* में पैदा हुए?",
        "bad_time": "समय समझ नहीं आया। HH:MM (जैसे 14:30) लिखें या *छोड़ें* दबाएं।",
        "bad_city": "*{city}* नहीं मिला। कोई नज़दीकी बड़ा शहर आज़माएं।",
        "onboard_done": (
            "सब तैयार! 🎉\n\n"
            "📅 {date}{time}\n"
            "📍 {city}\n\n"
            "/horoscope या /chart आज़माएं"
        ),
        "no_profile": "आपकी प्रोफ़ाइल अभी सेट नहीं है। पहले /start चलाएं!",
        "generating": "सितारों से पूछ रहे हैं… ✨",
        "horo_error": "अभी राशिफल नहीं बना सके। थोड़ी देर बाद आज़माएं।",
        "chart_error": "कुंडली नहीं बन सकी। थोड़ी देर बाद आज़माएं।",
        "sign_usage": "उपयोग: /sign <राशि>\nउदाहरण: /sign Aries\n\n{list}",
        "sign_unknown": "राशि *{sign}* नहीं मिली। /sign से पूरी सूची देखें।",
        "skip": "छोड़ें",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = T.get(lang, T["en"]).get(key, T["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text
