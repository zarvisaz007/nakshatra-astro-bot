"""
Admin panel for Nakshatra Astro Bot.
Run: venv/bin/python -m app.admin
Access: http://localhost:8080  (password from .env ADMIN_PASSWORD)
"""
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select, text

from app.config import settings
from app.database import AsyncSessionFactory
from app.models.user import User
from app.services.cache import get_redis

app = FastAPI(title="Nakshatra Admin", docs_url=None, redoc_url=None)
security = HTTPBasic()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

TIERS = ["free", "basic", "premium", "elite"]
FREE_MODELS = [
    "z-ai/glm-4.5-air:free",
    "qwen/qwen3-4b:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
]


# ── Auth ──────────────────────────────────────────────────────────────────────

def _check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ── .env helpers ──────────────────────────────────────────────────────────────

def _read_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def _write_env(updates: dict):
    env = _read_env()
    lines = []
    remaining = dict(updates)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k = stripped.partition("=")[0].strip()
                if k in remaining:
                    lines.append(f"{k}={remaining.pop(k)}")
                else:
                    lines.append(line)
            else:
                lines.append(line)
    for k, v in remaining.items():
        lines.append(f"{k}={v}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


# ── Redis helpers ─────────────────────────────────────────────────────────────

async def _redis_get_int(key: str) -> int:
    try:
        val = await get_redis().get(key)
        return int(val) if val else 0
    except Exception:
        return 0


async def _redis_count_keys(pattern: str) -> int:
    try:
        keys = await get_redis().keys(pattern)
        return len(keys)
    except Exception:
        return 0


async def _get_cmd_stats_today() -> list[tuple[str, int]]:
    today = date.today().isoformat()
    try:
        keys = await get_redis().keys(f"stats:cmd:*:{today}")
        results = []
        for key in keys:
            val = await get_redis().get(key)
            cmd = key.split(":")[2]
            results.append((cmd, int(val or 0)))
        return sorted(results, key=lambda x: x[1], reverse=True)
    except Exception:
        return []


async def _get_cmd_stats_total() -> list[tuple[str, int]]:
    try:
        keys = await get_redis().keys("stats:cmd:*:total")
        results = []
        for key in keys:
            val = await get_redis().get(key)
            cmd = key.split(":")[2]
            results.append((cmd, int(val or 0)))
        return sorted(results, key=lambda x: x[1], reverse=True)[:15]
    except Exception:
        return []


async def _get_daily_ai_calls(days: int = 7) -> list[tuple[str, int]]:
    result = []
    for i in range(days - 1, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        count = await _redis_get_int(f"stats:ai:calls:{d}")
        result.append((d[-5:], count))  # "MM-DD" format
    return result


async def _get_daily_cmd_volume(days: int = 7) -> list[tuple[str, int]]:
    result = []
    for i in range(days - 1, -1, -1):
        d = (date.today() - timedelta(days=i))
        today_str = d.isoformat()
        try:
            keys = await get_redis().keys(f"stats:cmd:*:{today_str}")
            total = 0
            for k in keys:
                v = await get_redis().get(k)
                total += int(v or 0)
            result.append((today_str[-5:], total))
        except Exception:
            result.append((today_str[-5:], 0))
    return result


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, _=Depends(_check_auth)):
    today = date.today()
    r = get_redis()

    async with AsyncSessionFactory() as session:
        total_users    = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
        onboarded      = (await session.execute(select(func.count()).select_from(User).where(User.birth_date.isnot(None)))).scalar() or 0
        hindi_users    = (await session.execute(select(func.count()).select_from(User).where(User.language == "hi"))).scalar() or 0
        paid_users     = (await session.execute(select(func.count()).select_from(User).where(User.subscription_tier != "free"))).scalar() or 0
        notif_users    = (await session.execute(select(func.count()).select_from(User).where(User.notifications_enabled == True))).scalar() or 0
        new_today      = (await session.execute(
            select(func.count()).select_from(User).where(
                func.date(User.created_at) == today.isoformat()
            )
        )).scalar() or 0
        new_week       = (await session.execute(
            select(func.count()).select_from(User).where(
                User.created_at >= (datetime.utcnow() - timedelta(days=7))
            )
        )).scalar() or 0
        tier_counts    = (await session.execute(
            select(User.subscription_tier, func.count()).group_by(User.subscription_tier)
        )).fetchall()
        recent_users   = (await session.execute(
            select(User).order_by(User.created_at.desc()).limit(8)
        )).scalars().all()
        top_askers     = (await session.execute(
            select(User).order_by(User.free_questions_used.desc()).limit(5)
        )).scalars().all()

    # Redis stats
    ai_today    = await _redis_get_int(f"stats:ai:calls:{today.isoformat()}")
    ai_total    = await _redis_get_int("stats:ai:calls:total")
    active_today = 0
    try:
        active_today = await r.scard(f"stats:users:active:{today.isoformat()}")
    except Exception:
        pass

    cmd_today   = await _get_cmd_stats_today()
    ai_7days    = await _get_daily_ai_calls(7)
    vol_7days   = await _get_daily_cmd_volume(7)

    # Redis health
    redis_ok = False
    try:
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    env = _read_env()
    tier_map = {t: 0 for t in TIERS}
    for tier, cnt in tier_counts:
        tier_map[tier or "free"] = cnt

    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": {
        "total_users": total_users,
        "onboarded": onboarded,
        "hindi_users": hindi_users,
        "english_users": onboarded - hindi_users,
        "paid_users": paid_users,
        "notif_users": notif_users,
        "new_today": new_today,
        "new_week": new_week,
        "active_today": active_today,
        "ai_today": ai_today,
        "ai_total": ai_total,
        "tier_map": tier_map,
        "cmd_today": cmd_today[:10],
        "ai_7days": ai_7days,
        "vol_7days": vol_7days,
        "recent_users": recent_users,
        "top_askers": top_askers,
        "redis_ok": redis_ok,
        "current_model": env.get("OPENROUTER_MODEL", settings.openrouter_model),
        "api_key_preview": (env.get("OPENROUTER_API_KEY", "")[:12] + "…") if env.get("OPENROUTER_API_KEY") else "not set",
    }})


# ── Users list ────────────────────────────────────────────────────────────────

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, _=Depends(_check_auth),
                     search: str = "", tier: str = "", lang: str = "", page: int = 1):
    PAGE = 50
    offset = (page - 1) * PAGE

    async with AsyncSessionFactory() as session:
        q = select(User).order_by(User.created_at.desc())
        if search:
            try:
                tid = int(search)
                q = select(User).where(User.telegram_id == tid)
            except ValueError:
                q = select(User).where(User.name.ilike(f"%{search}%"))
        if tier:
            q = q.where(User.subscription_tier == tier)
        if lang:
            q = q.where(User.language == lang)

        total_q = select(func.count()).select_from(q.subquery())
        total_count = (await session.execute(total_q)).scalar() or 0
        users = (await session.execute(q.offset(offset).limit(PAGE))).scalars().all()

    return templates.TemplateResponse("users.html", {
        "request": request, "users": users, "search": search,
        "tier_filter": tier, "lang_filter": lang,
        "page": page, "total": total_count, "page_size": PAGE,
        "tiers": TIERS,
    })


# ── User detail ───────────────────────────────────────────────────────────────

@app.get("/users/{telegram_id}", response_class=HTMLResponse)
async def user_detail(request: Request, telegram_id: int, _=Depends(_check_auth),
                      msg: str = ""):
    async with AsyncSessionFactory() as session:
        u = (await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if not u:
            raise HTTPException(404, "User not found")

    # Redis: command usage for this user would need per-user tracking (not yet).
    # Show AI questions used instead.
    return templates.TemplateResponse("user_detail.html", {
        "request": request, "u": u, "tiers": TIERS, "msg": msg,
    })


@app.post("/users/{telegram_id}/tier")
async def update_tier(telegram_id: int, _=Depends(_check_auth),
                      tier: str = Form(...)):
    if tier not in TIERS:
        raise HTTPException(400, "Invalid tier")
    async with AsyncSessionFactory() as session:
        u = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if not u:
            raise HTTPException(404)
        u.subscription_tier = tier
        await session.commit()
    return RedirectResponse(f"/users/{telegram_id}?msg=tier_saved", status_code=303)


@app.post("/users/{telegram_id}/reset-questions")
async def reset_questions(telegram_id: int, _=Depends(_check_auth)):
    async with AsyncSessionFactory() as session:
        u = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if not u:
            raise HTTPException(404)
        u.free_questions_used = 0
        await session.commit()
    return RedirectResponse(f"/users/{telegram_id}?msg=questions_reset", status_code=303)


@app.post("/users/{telegram_id}/toggle-notifications")
async def toggle_notifications(telegram_id: int, _=Depends(_check_auth)):
    async with AsyncSessionFactory() as session:
        u = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if not u:
            raise HTTPException(404)
        u.notifications_enabled = not u.notifications_enabled
        await session.commit()
    return RedirectResponse(f"/users/{telegram_id}?msg=notif_toggled", status_code=303)


@app.post("/users/{telegram_id}/delete")
async def delete_user(telegram_id: int, _=Depends(_check_auth),
                      confirm: str = Form("")):
    if confirm != "DELETE":
        return RedirectResponse(f"/users/{telegram_id}?msg=confirm_required", status_code=303)
    async with AsyncSessionFactory() as session:
        u = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if u:
            await session.delete(u)
            await session.commit()
    return RedirectResponse("/users?msg=deleted", status_code=303)


# ── Analytics ─────────────────────────────────────────────────────────────────

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, _=Depends(_check_auth)):
    # New users per day (last 14 days)
    user_growth = []
    async with AsyncSessionFactory() as session:
        for i in range(13, -1, -1):
            d = date.today() - timedelta(days=i)
            cnt = (await session.execute(
                select(func.count()).select_from(User).where(
                    func.date(User.created_at) == d.isoformat()
                )
            )).scalar() or 0
            user_growth.append((d.strftime("%d %b"), cnt))

        # Tier breakdown
        tier_data = (await session.execute(
            select(User.subscription_tier, func.count()).group_by(User.subscription_tier)
        )).fetchall()

        # Language breakdown
        lang_data = (await session.execute(
            select(User.language, func.count()).group_by(User.language)
        )).fetchall()

    cmd_today = await _get_cmd_stats_today()
    cmd_total = await _get_cmd_stats_total()
    ai_7days  = await _get_daily_ai_calls(14)
    vol_7days = await _get_daily_cmd_volume(14)

    tier_map = {t: 0 for t in TIERS}
    for t, c in tier_data:
        tier_map[t or "free"] = c
    lang_map = {}
    for l, c in lang_data:
        lang_map[l or "en"] = c

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "user_growth": user_growth,
        "cmd_today": cmd_today,
        "cmd_total": cmd_total,
        "ai_7days": ai_7days,
        "vol_7days": vol_7days,
        "tier_map": tier_map,
        "lang_map": lang_map,
    })


# ── Redis / Cache monitor ─────────────────────────────────────────────────────

@app.get("/cache", response_class=HTMLResponse)
async def cache_page(request: Request, _=Depends(_check_auth)):
    r = get_redis()
    info = {}
    redis_ok = False
    try:
        raw = await r.info()
        redis_ok = True
        info = {
            "version":       raw.get("redis_version", "?"),
            "uptime_days":   raw.get("uptime_in_days", 0),
            "memory_used":   raw.get("used_memory_human", "?"),
            "memory_peak":   raw.get("used_memory_peak_human", "?"),
            "clients":       raw.get("connected_clients", 0),
            "total_cmds":    raw.get("total_commands_processed", 0),
            "hits":          raw.get("keyspace_hits", 0),
            "misses":        raw.get("keyspace_misses", 0),
            "total_keys":    sum(
                int(v.get("keys", 0))
                for v in raw.get("keyspace", {}).values()
                if isinstance(v, dict)
            ),
        }
        hit_total = info["hits"] + info["misses"]
        info["hit_rate"] = f"{100 * info['hits'] // hit_total}%" if hit_total else "N/A"
    except Exception as e:
        info["error"] = str(e)

    patterns = [
        ("horoscope:*",         "Daily horoscope cache"),
        ("career:*",            "Career readings"),
        ("marriage:*",          "Marriage readings"),
        ("wealth:*",            "Wealth readings"),
        ("spiritual:*",         "Spiritual guidance"),
        ("numerology:*",        "Numerology readings"),
        ("milestones:*",        "Milestones readings (7-day)"),
        ("stats:cmd:*",         "Command usage counters"),
        ("stats:ai:*",          "AI call counters"),
        ("stats:users:active:*","Active user sets"),
        ("sched:*",             "Scheduler dedup keys"),
        ("fsm:*",               "Aiogram FSM states"),
    ]
    key_counts = []
    for pattern, label in patterns:
        count = await _redis_count_keys(pattern)
        key_counts.append({"pattern": pattern, "label": label, "count": count})

    # Recent AI calls
    ai_calls = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        count = await _redis_get_int(f"stats:ai:calls:{d.isoformat()}")
        ai_calls.append({"date": d.strftime("%d %b"), "count": count})

    return templates.TemplateResponse("cache.html", {
        "request": request,
        "redis_ok": redis_ok,
        "info": info,
        "key_counts": key_counts,
        "ai_calls": ai_calls,
    })


@app.post("/cache/flush-pattern")
async def flush_pattern(request: Request, _=Depends(_check_auth),
                        pattern: str = Form(...)):
    """Flush all keys matching a pattern."""
    safe_patterns = ["horoscope:*", "career:*", "marriage:*", "wealth:*",
                     "spiritual:*", "numerology:*", "milestones:*"]
    if pattern not in safe_patterns:
        return RedirectResponse("/cache?msg=unsafe", status_code=303)
    r = get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)
    return RedirectResponse(f"/cache?msg=flushed_{len(keys)}", status_code=303)


# ── Settings ──────────────────────────────────────────────────────────────────

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, _=Depends(_check_auth), saved: str = ""):
    env = _read_env()
    return templates.TemplateResponse("settings.html", {
        "request": request, "env": env, "saved": saved,
        "free_models": FREE_MODELS,
    })


@app.post("/settings")
async def save_settings(request: Request, _=Depends(_check_auth),
                        openrouter_api_key: str = Form(""),
                        openrouter_model: str = Form(""),
                        telegram_bot_token: str = Form(""),
                        admin_password: str = Form("")):
    updates = {}
    if openrouter_api_key.strip():
        updates["OPENROUTER_API_KEY"] = openrouter_api_key.strip()
    if openrouter_model.strip():
        updates["OPENROUTER_MODEL"] = openrouter_model.strip()
    if telegram_bot_token.strip():
        updates["TELEGRAM_BOT_TOKEN"] = telegram_bot_token.strip()
    if admin_password.strip():
        updates["ADMIN_PASSWORD"] = admin_password.strip()
    if updates:
        _write_env(updates)
    return RedirectResponse("/settings?saved=1", status_code=303)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    r = get_redis()
    redis_ok = False
    try:
        await r.ping()
        redis_ok = True
    except Exception:
        pass
    async with AsyncSessionFactory() as session:
        db_users = (await session.execute(select(func.count()).select_from(User))).scalar()
    return {"status": "ok", "time": datetime.utcnow().isoformat(),
            "redis": redis_ok, "total_users": db_users}


def run():
    uvicorn.run(app, host="127.0.0.1", port=settings.admin_port, log_level="warning")


if __name__ == "__main__":
    run()
