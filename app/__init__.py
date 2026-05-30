"""
app/__init__.py — Vasıta Application Factory

Kullanım:
    from app import create_app
    app = create_app('development')
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from config import config

# Eklenti nesneleri — uygulama bağımsız olarak oluşturulur,
# create_app() içinde app'e bağlanır.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name: str = "default") -> Flask:
    """Vasıta Flask uygulamasını oluşturur ve döndürür."""

    app = Flask(__name__)

    # Yapılandırmayı yükle
    app.config.from_object(config[config_name])

    # Eklentileri uygulamaya bağla
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprint'leri kaydet
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from app.profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix="/profile")

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    return app
