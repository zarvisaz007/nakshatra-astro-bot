import logging

from app.services.horoscope import _call_ai

logger = logging.getLogger(__name__)

_DREAM_PROMPT = {
    "en": (
        "You are a Vedic dream interpreter. Interpret this dream: \"{dream}\"\n\n"
        "The dreamer: {name}, Moon in {moon_sign} ({nakshatra}), current Mahadasha: {dasha}.\n\n"
        "Provide:\n"
        "1. Core symbolism (what key elements mean in Vedic tradition)\n"
        "2. Message from the universe (what this dream is telling them)\n"
        "3. Planetary influence (which planet is sending this message)\n"
        "4. Auspicious/inauspicious? Any remedies needed?\n\n"
        "~200 words. Mystical yet grounded in Vedic tradition."
    ),
    "hi": (
        "आप एक वैदिक स्वप्न विश्लेषक हैं। इस स्वप्न की व्याख्या करें: \"{dream}\"\n\n"
        "स्वप्नदृष्टा: {name}, चंद्रमा {moon_sign} में ({nakshatra}), वर्तमान महादशा: {dasha}।\n\n"
        "बताएं:\n"
        "1. मूल प्रतीकवाद (वैदिक परंपरा में प्रमुख तत्वों का अर्थ)\n"
        "2. ब्रह्मांड का संदेश (यह स्वप्न क्या बता रहा है)\n"
        "3. ग्रह प्रभाव (कौन सा ग्रह यह संदेश भेज रहा है)\n"
        "4. शुभ/अशुभ? कोई उपाय आवश्यक है?\n\n"
        "~200 शब्द। वैदिक परंपरा में आधारित रहस्यमय विश्लेषण।"
    ),
}


async def interpret_dream(
    dream: str,
    name: str,
    moon_sign: str,
    nakshatra: str,
    dasha: str,
    lang: str = "en",
) -> str:
    prompt = _DREAM_PROMPT.get(lang, _DREAM_PROMPT["en"]).format(
        dream=dream,
        name=name,
        moon_sign=moon_sign,
        nakshatra=nakshatra,
        dasha=dasha,
    )
    logger.info("Interpreting dream for user=%s lang=%s", name, lang)
    return await _call_ai(prompt)
