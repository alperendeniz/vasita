"""
app/admin/__init__.py — Admin blueprint tanımı

Sadece yöneticilerin erişebileceği rotaları içerir.
URL öneki: /admin
"""

from flask import Blueprint

admin = Blueprint("admin", __name__)

from app.admin import routes  # noqa: E402, F401
