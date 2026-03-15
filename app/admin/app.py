"""
Admin panel for Nakshatra Astro Bot.
Run: venv/bin/python -m app.admin
Access: http://localhost:8080  (password from .env ADMIN_PASSWORD)
"""
import os
import re
from datetime import datetime
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

app = FastAPI(title="Nakshatra Admin", docs_url=None, redoc_url=None)
security = HTTPBasic()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ENV_FILE = Path(__file__).parent.parent.parent / ".env"


def _check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


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
    env.update(updates)
    lines = []
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k = stripped.partition("=")[0].strip()
                if k in updates:
                    lines.append(f"{k}={updates[k]}")
                    updates.pop(k)
                else:
                    lines.append(line)
            else:
                lines.append(line)
    for k, v in updates.items():
        lines.append(f"{k}={v}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(_check_auth)):
    async with AsyncSessionFactory() as session:
        total_users = (await session.execute(select(func.count()).select_from(User))).scalar()
        onboarded = (await session.execute(
            select(func.count()).select_from(User).where(User.birth_date.isnot(None))
        )).scalar()
        hindi_users = (await session.execute(
            select(func.count()).select_from(User).where(User.language == "hi")
        )).scalar()
        paid_users = (await session.execute(
            select(func.count()).select_from(User).where(User.subscription_tier != "free")
        )).scalar()
        top_askers = (await session.execute(
            select(User.name, User.telegram_id, User.free_questions_used)
            .order_by(User.free_questions_used.desc()).limit(5)
        )).fetchall()

    env = _read_env()
    stats = {
        "total_users": total_users,
        "onboarded": onboarded,
        "hindi_users": hindi_users,
        "english_users": (onboarded or 0) - (hindi_users or 0),
        "paid_users": paid_users,
        "top_askers": top_askers,
        "current_model": env.get("OPENROUTER_MODEL", settings.openrouter_model),
        "api_key_preview": (env.get("OPENROUTER_API_KEY", "")[:12] + "...") if env.get("OPENROUTER_API_KEY") else "not set",
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, username: str = Depends(_check_auth), saved: str = ""):
    env = _read_env()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "env": env,
        "saved": saved,
        "free_models": [
            "z-ai/glm-4.5-air:free",
            "qwen/qwen3-4b:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-3-27b-it:free",
            "openai/gpt-oss-20b:free",
        ],
    })


@app.post("/settings")
async def save_settings(
    request: Request,
    username: str = Depends(_check_auth),
    openrouter_api_key: str = Form(""),
    openrouter_model: str = Form(""),
    telegram_bot_token: str = Form(""),
    admin_password: str = Form(""),
):
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

    return RedirectResponse(url="/settings?saved=1", status_code=303)


@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, username: str = Depends(_check_auth), search: str = ""):
    async with AsyncSessionFactory() as session:
        query = select(User).order_by(User.created_at.desc()).limit(50)
        if search:
            try:
                tid = int(search)
                query = select(User).where(User.telegram_id == tid)
            except ValueError:
                query = select(User).where(User.name.ilike(f"%{search}%"))
        users = (await session.execute(query)).scalars().all()

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "search": search,
    })


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


def run():
    uvicorn.run(app, host="127.0.0.1", port=settings.admin_port, log_level="warning")


if __name__ == "__main__":
    run()
