"""
app/main/__init__.py — Ana blueprint tanımı

Ana sayfa, araç listeleme ve genel içerik route'ları bu blueprint altında yer alacak.
"""

from flask import Blueprint

main = Blueprint("main", __name__)

from app.main import routes  # noqa: E402, F401
