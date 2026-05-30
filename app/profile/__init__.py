"""
app/profile/__init__.py — Profil blueprint tanımı

Kullanıcı profil görüntüleme ve düzenleme rotaları bu blueprint altında yer alır.
URL öneki: /profile
"""

from flask import Blueprint

profile = Blueprint("profile", __name__)

from app.profile import routes  # noqa: E402, F401
