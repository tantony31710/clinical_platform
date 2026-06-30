"""
core/auth.py — Authentication and rate-limiting middleware for the Clinical Platform.

Provides:
  - login_required decorator: blocks unauthenticated access to any route.
  - get_current_patient_id: safely extracts patient ID from session (never from request).
  - Simple in-memory rate limiter to protect expensive ML inference endpoints.
"""
import os
import time
import hashlib
import logging
from collections import defaultdict
from functools import wraps
from typing import Callable

from flask import session, request, jsonify, redirect, url_for

logger = logging.getLogger(__name__)

# ── Session secret ────────────────────────────────────────────────────────────
# Must be set via environment variable. A missing secret is a hard startup error.
SECRET_KEY: str | None = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "[Auth] SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )


# ── Rate limiter ──────────────────────────────────────────────────────────────
# Simple sliding-window rate limiter. In production, replace with Redis-backed
# flask-limiter for multi-process deployments.

_rate_store: dict[str, list[float]] = defaultdict(list)

def _get_client_key() -> str:
    """Use a hash of the IP so we don't store raw IPs in memory."""
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()


def rate_limit(max_calls: int = 30, window_seconds: int = 60):
    """
    Decorator that limits a route to `max_calls` requests per `window_seconds`
    per client IP. Returns 429 when the limit is exceeded.

    Usage:
        @app.route('/api/assess', methods=['POST'])
        @login_required
        @rate_limit(max_calls=10, window_seconds=60)
        def api_assess():
            ...
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{fn.__name__}:{_get_client_key()}"
            now = time.time()
            window_start = now - window_seconds

            # Purge timestamps outside the window
            _rate_store[key] = [t for t in _rate_store[key] if t > window_start]

            if len(_rate_store[key]) >= max_calls:
                logger.warning("[RateLimit] Limit exceeded for key %s", key[:16])
                return jsonify({
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Maximum {max_calls} per {window_seconds}s.",
                    "retry_after": int(window_seconds - (now - _rate_store[key][0])),
                }), 429

            _rate_store[key].append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ── Authentication helpers ────────────────────────────────────────────────────

def login_required(fn: Callable) -> Callable:
    """
    Decorator that requires the user to be logged in.
    API routes (starting with /api/) return 401 JSON.
    UI routes redirect to the login page.

    Usage:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("patient_id"):
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "unauthenticated",
                    "message": "Authentication required. Please log in.",
                }), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def get_current_patient_id() -> str | None:
    """
    Returns the authenticated patient's ID from the server-side session.
    This is the ONLY safe source of patient_id — never use request args/body.
    """
    return session.get("patient_id")


def set_session(patient_id: str, role: str = "patient") -> None:
    """Writes patient identity into the server-side session after successful login."""
    session["patient_id"] = patient_id
    session["role"] = role
    session.permanent = True  # Respects app.permanent_session_lifetime


def clear_session() -> None:
    """Clears all session data on logout."""
    session.clear()
