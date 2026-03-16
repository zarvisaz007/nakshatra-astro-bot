import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"


async def get_palm_reading(
    photo_base64: str,
    name: str,
    lagna: str,
    nakshatra: str,
    dasha: str,
    lang: str = "en",
) -> str:
    """Send palm image to vision AI and get Vedic palm reading."""
    client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    prompt_en = (
        f"You are a Vedic palmist. Analyze this palm image for {name}. "
        f"Vedic birth context: Lagna {lagna}, Nakshatra {nakshatra}, Mahadasha {dasha}.\n\n"
        "Read these lines:\n"
        "1. Life Line — vitality, health, major life changes\n"
        "2. Head Line — intellect, decision-making, career\n"
        "3. Heart Line — emotions, relationships, love\n"
        "4. Fate/Saturn Line — career, destiny\n"
        "5. Mount of Jupiter, Venus, Moon — personality\n\n"
        "~200 words. Vedic perspective. Specific predictions and timing where visible. "
        "Warm and encouraging tone."
    )

    prompt_hi = (
        f"आप एक वैदिक हस्तरेखा विशेषज्ञ हैं। {name} की हथेली देखें। "
        f"जन्म: लग्न {lagna}, नक्षत्र {nakshatra}, महादशा {dasha}।\n\n"
        "इन रेखाओं का विश्लेषण करें: जीवन रेखा, मस्तिष्क रेखा, हृदय रेखा, भाग्य रेखा। "
        "~200 शब्द। वैदिक दृष्टिकोण से।"
    )

    prompt = prompt_hi if lang == "hi" else prompt_en

    logger.info("Requesting palm reading for %s (lang=%s)", name, lang)

    response = await client.chat.completions.create(
        model=_VISION_MODEL,
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{photo_base64}"}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return (response.choices[0].message.content or "").strip()
