"""
app/auth/__init__.py — Kimlik doğrulama blueprint tanımı

Kayıt, giriş ve çıkış route'ları bu blueprint altında yer alacak.
URL öneki: /auth
"""

from flask import Blueprint

auth = Blueprint("auth", __name__)

from app.auth import routes  # noqa: E402, F401
