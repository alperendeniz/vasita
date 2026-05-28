"""
config.py — Vasıta uygulama yapılandırması
Tüm hassas değerler .env üzerinden os.environ'dan okunur.
"""

import os
from dotenv import load_dotenv

# Proje kök dizininde .env varsa yükle
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Ortak temel yapılandırma."""

    # Güvenlik
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-degistir")

    # Yolu güvenli bir şekilde birleştirip, Windows backslash'lerini düzeltiyoruz
    db_path = os.path.join(basedir, "instance", "vasita.db").replace('\\', '/')

    # Veritabanı
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{db_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF koruması (Flask-WTF)
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Geliştirme ortamı — DEBUG açık, SQLite."""

    DEBUG = True


class ProductionConfig(Config):
    """Üretim ortamı — DEBUG kapalı."""

    DEBUG = False
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    """Test ortamı — geçici bellek içi veritabanı."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Form testlerini kolaylaştırır


# İsim → sınıf eşleme; create_app() tarafından kullanılır
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
