"""
card_service.py — Pillow image generation for Destiny Report Card (and future Compatibility Card).
"""

import asyncio
import io
import random
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
BG_DARK    = (10,  10,  46)
BG_CARD    = (20,  20,  60)
GOLD       = (255, 215,  0)
GOLD_LIGHT = (255, 235, 100)
WHITE      = (255, 255, 255)
GRAY       = (180, 180, 200)
PURPLE     = (147, 112, 219)
CYAN       = (100, 200, 255)

# ---------------------------------------------------------------------------
# Font paths
# ---------------------------------------------------------------------------
_FONT_BOLD    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
_FONT_ITALIC  = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

# ---------------------------------------------------------------------------
# Lucky color RGB swatches
# ---------------------------------------------------------------------------
COLOR_RGB: dict[str, tuple[int, int, int]] = {
    "White":  (255, 255, 255),
    "Pink":   (255, 182, 193),
    "Red":    (220,  50,  50),
    "Green":  ( 50, 180,  50),
    "Yellow": (255, 215,   0),
    "Blue":   ( 70, 130, 180),
    "Purple": (147, 112, 219),
}


# ---------------------------------------------------------------------------
# Font loader helper
# ---------------------------------------------------------------------------

def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Internal synchronous drawing function
# ---------------------------------------------------------------------------

def _draw_report_card(
    name: str,
    dob: str,
    city: str,
    lagna: str,
    rashi: str,
    nakshatra: str,
    pada: int,
    dasha: str,
    life_path: int,
    life_path_planet: str,
    destiny_num: int,
    lucky_num: int,
    lucky_color: str,
    sign_symbol: str,
) -> bytes:
    W, H = 900, 500

    # --- Canvas ---
    img  = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # --- Fonts ---
    f_brand  = _font(_FONT_BOLD,    18)
    f_title  = _font(_FONT_BOLD,    22)
    f_label  = _font(_FONT_REGULAR, 15)
    f_value  = _font(_FONT_BOLD,    15)
    f_small  = _font(_FONT_REGULAR, 13)
    f_footer = _font(_FONT_ITALIC,  12)

    # --- Background card rectangle ---
    card_margin = 18
    draw.rounded_rectangle(
        [card_margin, card_margin, W - card_margin, H - card_margin],
        radius=14,
        fill=BG_CARD,
        outline=GOLD,
        width=1,
    )

    # --- Stars ---
    rng = random.Random(42)   # fixed seed so stars are deterministic
    for _ in range(45):
        sx = rng.randint(card_margin + 5, W - card_margin - 5)
        sy = rng.randint(card_margin + 5, H - card_margin - 5)
        r  = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)

    # --- Brand header ---
    brand_text = "\u2726  NAKSHATRA ASTRO  \u2726"
    bb = draw.textbbox((0, 0), brand_text, font=f_brand)
    brand_w = bb[2] - bb[0]
    draw.text(((W - brand_w) // 2, 34), brand_text, font=f_brand, fill=GOLD)

    # --- Top divider ---
    draw.line([(60, 62), (W - 60, 62)], fill=GOLD, width=1)

    # --- Title ---
    title_text = "\U0001f52f  YOUR COSMIC BLUEPRINT  \U0001f52f"
    tb = draw.textbbox((0, 0), title_text, font=f_title)
    title_w = tb[2] - tb[0]
    draw.text(((W - title_w) // 2, 74), title_text, font=f_title, fill=GOLD_LIGHT)

    # --- Section divider below title ---
    draw.line([(60, 108), (W - 60, 108)], fill=GOLD, width=1)

    # --- Truncate long name ---
    display_name = name[:20] if len(name) > 20 else name

    # --- LEFT COLUMN content ---
    lx = 60
    ly = 122

    def draw_field(x: int, y: int, label: str, value: str, lc=GRAY, vc=WHITE) -> int:
        """Draw 'label: value' pair, return new y."""
        draw.text((x, y), label + ": ", font=f_label, fill=lc)
        lw = draw.textbbox((0, 0), label + ": ", font=f_label)[2]
        draw.text((x + lw, y), value, font=f_value, fill=vc)
        return y + 24

    ly = draw_field(lx, ly, "Name", display_name)
    ly = draw_field(lx, ly, "Born", dob)
    ly = draw_field(lx, ly, "\U0001f4cd", city, lc=CYAN, vc=CYAN)

    # Divider
    ly += 6
    draw.line([(lx, ly), (lx + 360, ly)], fill=GOLD, width=1)
    ly += 10

    ly = draw_field(lx, ly, "Life Path", f"{life_path}  ({life_path_planet})", vc=PURPLE)
    ly = draw_field(lx, ly, "Destiny",   str(destiny_num), vc=GOLD_LIGHT)

    # --- RIGHT COLUMN content ---
    rx = 490
    ry = 122

    ry = draw_field(rx, ry, "\u2b50 Nakshatra", nakshatra, vc=GOLD_LIGHT)
    ry = draw_field(rx, ry, "\U0001f319 Rashi",     rashi,     vc=CYAN)
    ry = draw_field(rx, ry, "\U0001f305 Lagna",    lagna,     vc=WHITE)
    ry = draw_field(rx, ry, "\U0001f300 Dasha",    dasha,     vc=PURPLE)

    # Divider
    ry += 6
    draw.line([(rx, ry), (rx + 360, ry)], fill=GOLD, width=1)
    ry += 10

    ry = draw_field(rx, ry, "Lucky No",    str(lucky_num), vc=GOLD)

    # Lucky color with swatch
    lc_label = "Lucky Color: "
    draw.text((rx, ry), lc_label, font=f_label, fill=GRAY)
    lc_lw = draw.textbbox((0, 0), lc_label, font=f_label)[2]
    swatch_x = rx + lc_lw
    swatch_y = ry + 1
    swatch_rgb = COLOR_RGB.get(lucky_color, (255, 255, 255))
    draw.rectangle([swatch_x, swatch_y, swatch_x + 40, swatch_y + 14], fill=swatch_rgb)
    # Thin border around swatch
    draw.rectangle([swatch_x, swatch_y, swatch_x + 40, swatch_y + 14], outline=GRAY, width=1)
    draw.text((swatch_x + 46, ry), lucky_color, font=f_value, fill=WHITE)

    # --- Bottom divider ---
    draw.line([(60, H - 70), (W - 60, H - 70)], fill=GOLD, width=1)

    # --- Bottom center: nakshatra pada + rashi symbol ---
    bottom_center = f"{nakshatra} pada {pada}  \u2022  {sign_symbol} {rashi}"
    bc_bb = draw.textbbox((0, 0), bottom_center, font=f_small)
    bc_w  = bc_bb[2] - bc_bb[0]
    draw.text(((W - bc_w) // 2, H - 56), bottom_center, font=f_small, fill=GRAY)

    # --- Bottom right: handle ---
    handle = "@Nakshatra_Astrobot"
    hb = draw.textbbox((0, 0), handle, font=f_footer)
    handle_w = hb[2] - hb[0]
    draw.text((W - card_margin - handle_w - 8, H - 40), handle, font=f_footer, fill=GRAY)

    # --- Render to bytes ---
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------

async def generate_report_card(
    name: str,
    dob: str,
    city: str,
    lagna: str,
    rashi: str,
    nakshatra: str,
    pada: int,
    dasha: str,
    life_path: int,
    life_path_planet: str,
    destiny_num: int,
    lucky_num: int,
    lucky_color: str,
    sign_symbol: str,
) -> bytes:
    """Generate destiny report card image. Returns PNG bytes."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _draw_report_card,
        name, dob, city, lagna, rashi, nakshatra, pada, dasha,
        life_path, life_path_planet, destiny_num, lucky_num, lucky_color, sign_symbol,
    )


# ---------------------------------------------------------------------------
# Compatibility Card — color palette
# ---------------------------------------------------------------------------
_COMPAT_BG        = (20,  5,  35)
_COMPAT_ROSE      = (220, 80, 120)
_COMPAT_HEART_RED = (220, 50,  80)
_COMPAT_DARK_GRAY = (80,  80, 100)


def _score_bar_color(score: int) -> tuple[int, int, int]:
    if score <= 17:
        return (200, 50, 50)
    elif score <= 24:
        return (220, 130, 50)
    elif score <= 31:
        return (255, 200, 0)
    else:
        return (50, 200, 100)


# ---------------------------------------------------------------------------
# Internal synchronous drawing function — compatibility card
# ---------------------------------------------------------------------------

def _draw_compat_card(
    name1: str,
    name2: str,
    nakshatra1: str,
    rashi1: str,
    nakshatra2: str,
    rashi2: str,
    score: int,
    compatibility: str,
    details: dict,
) -> bytes:
    W, H = 900, 500
    img = Image.new("RGB", (W, H), color=_COMPAT_BG)
    draw = ImageDraw.Draw(img)

    # --- Fonts ---
    f_title    = _font(_FONT_BOLD,    22)
    f_name     = _font(_FONT_BOLD,    28)
    f_sub      = _font(_FONT_REGULAR, 16)
    f_score    = _font(_FONT_BOLD,    36)
    f_label    = _font(_FONT_BOLD,    18)
    f_small    = _font(_FONT_REGULAR, 13)
    f_tiny     = _font(_FONT_REGULAR, 11)
    f_wm       = _font(_FONT_REGULAR, 12)

    # --- Background stars (30-40 random white dots) ---
    rng = random.Random(99)
    for _ in range(35):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        r  = rng.randint(1, 2)
        br = rng.randint(120, 255)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(br, br, br))

    # --- Top title: KUNDLI COMPATIBILITY ---
    title_text = "  KUNDLI COMPATIBILITY  "
    bb = draw.textbbox((0, 0), title_text, font=f_title)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, 22), title_text, fill=GOLD, font=f_title)

    # --- Watermark top-right ---
    wm_text = "@Nakshatra_Astrobot"
    wb = draw.textbbox((0, 0), wm_text, font=f_wm)
    ww = wb[2] - wb[0]
    draw.text((W - ww - 12, 24), wm_text, fill=GRAY, font=f_wm)

    # --- Names row ---
    name_y = 72
    n1 = name1[:18]
    n2 = name2[:18]
    draw.text((60, name_y), n1, fill=WHITE, font=f_name)

    heart = "\u2764"
    hb = draw.textbbox((0, 0), heart, font=f_name)
    hw = hb[2] - hb[0]
    draw.text(((W - hw) // 2, name_y), heart, fill=_COMPAT_HEART_RED, font=f_name)

    n2b = draw.textbbox((0, 0), n2, font=f_name)
    n2w = n2b[2] - n2b[0]
    draw.text((W - 60 - n2w, name_y), n2, fill=WHITE, font=f_name)

    # --- Nakshatra / Rashi sub-labels ---
    sub_y = name_y + 40
    draw.text((60, sub_y),       nakshatra1, fill=_COMPAT_ROSE, font=f_sub)
    draw.text((60, sub_y + 20),  rashi1,     fill=GRAY,         font=f_sub)

    nb2 = draw.textbbox((0, 0), nakshatra2, font=f_sub)
    rb2 = draw.textbbox((0, 0), rashi2,     font=f_sub)
    draw.text((W - 60 - (nb2[2] - nb2[0]), sub_y),       nakshatra2, fill=_COMPAT_ROSE, font=f_sub)
    draw.text((W - 60 - (rb2[2] - rb2[0]), sub_y + 20),  rashi2,     fill=GRAY,         font=f_sub)

    # --- Divider ---
    div_y = sub_y + 56
    draw.line([(60, div_y), (W - 60, div_y)], fill=_COMPAT_ROSE, width=2)

    # --- COMPATIBILITY SCORE label + numeric score ---
    sc_label_y = div_y + 14
    draw.text((60, sc_label_y), "COMPATIBILITY SCORE", fill=GRAY, font=f_label)

    score_text = f"{score}/36"
    sb = draw.textbbox((0, 0), score_text, font=f_score)
    stw = sb[2] - sb[0]
    draw.text((W - 60 - stw, sc_label_y - 4), score_text, fill=GOLD, font=f_score)

    # --- Score progress bar ---
    bar_y = sc_label_y + 36
    bar_x, bar_w, bar_h, bar_r = 60, 700, 20, 8
    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                            radius=bar_r, fill=_COMPAT_DARK_GRAY)
    filled_w = max(int((score / 36) * bar_w), bar_r * 2)
    draw.rounded_rectangle([bar_x, bar_y, bar_x + filled_w, bar_y + bar_h],
                            radius=bar_r, fill=_score_bar_color(score))

    # --- Compatibility label ---
    compat_map = {
        "Excellent": "\u2b50 Excellent Match!",
        "Good":      "\u2b50 Good Match",
        "Average":   "\u2b50 Average Compatibility",
        "Poor":      "\u2b50 Below Average",
    }
    compat_display = compat_map.get(compatibility, f"\u2b50 {compatibility}")
    compat_y = bar_y + bar_h + 12
    draw.text((60, compat_y), compat_display, fill=GOLD, font=f_label)

    # --- Guna details row ---
    guna_y = compat_y + 34
    x_cursor = 60
    for guna_name, (got, max_) in list(details.items())[:8]:
        item_str = f"{guna_name} {got}/{max_}"
        draw.text((x_cursor, guna_y), item_str, fill=GRAY, font=f_small)
        ib = draw.textbbox((0, 0), item_str, font=f_small)
        x_cursor += (ib[2] - ib[0]) + 18
        if x_cursor > W - 80:
            break

    # --- Bottom divider + footer ---
    foot_y = H - 40
    draw.line([(60, foot_y), (W - 60, foot_y)], fill=_COMPAT_DARK_GRAY, width=1)
    footer = "Generated by Nakshatra Astro  \u2022  nakshatra-astro-bot"
    fb = draw.textbbox((0, 0), footer, font=f_tiny)
    fw = fb[2] - fb[0]
    draw.text(((W - fw) // 2, foot_y + 10), footer, fill=GRAY, font=f_tiny)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Public async API — compatibility card
# ---------------------------------------------------------------------------

async def generate_compatibility_card(
    name1: str,
    name2: str,
    nakshatra1: str,
    rashi1: str,
    nakshatra2: str,
    rashi2: str,
    score: int,           # out of 36
    compatibility: str,   # "Excellent", "Good", "Average", "Poor"
    details: dict,        # guna details dict from guna_milan
) -> bytes:
    """
    Generate a 900x500 PNG compatibility card and return as bytes.
    Runs the blocking Pillow draw in a thread executor.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _draw_compat_card,
        name1, name2,
        nakshatra1, rashi1,
        nakshatra2, rashi2,
        score, compatibility, details,
    )
