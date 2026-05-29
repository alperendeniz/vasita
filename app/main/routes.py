"""
app/main/routes.py — Ana blueprint route'ları

Henüz tam içerik eklenmemiştir.
İlerleyen aşamalarda araç detay, arama gibi view fonksiyonları buraya eklenecek.
"""

from flask import render_template

from app.main import main


@main.route("/")
def index():
    """Ana sayfa — geçici yer tutucu."""
    return render_template("main/index.html")

