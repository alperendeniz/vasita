"""
run.py — Vasıta geliştirme sunucusu başlatıcı.

Kullanım:
    flask --app run shell          # interaktif Python kabuğu
    flask --app run run            # sunucuyu başlat
    python run.py                  # alternatif başlatma
"""

from app import create_app

app = create_app("development")

if __name__ == "__main__":
    app.run()
