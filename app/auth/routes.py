"""
app/auth/routes.py — Kimlik doğrulama blueprint route'ları

Route'lar:
    GET  /auth/register  — Kayıt formunu göster
    POST /auth/register  — Formu işle, kullanıcı oluştur, login'e yönlendir
    GET  /auth/login     — Giriş formunu göster
    POST /auth/login     — Formu işle, oturum aç, ana sayfaya yönlendir
    GET  /auth/logout    — Oturumu kapat, ana sayfaya yönlendir
"""

from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


# ---------------------------------------------------------------------------
# Kayıt
# ---------------------------------------------------------------------------

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Yeni kullanıcı kaydı.

    GET  → Kayıt formunu render et.
    POST → Formu doğrula; başarılıysa kullanıcıyı oluştur ve login'e yönlendir.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        clean_email = form.email.data.strip().lower()
        user = User(username=form.username.data, email=clean_email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Kaydınız tamamlandı! Şimdi giriş yapabilirsiniz.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Kayıt Ol", form=form)


# ---------------------------------------------------------------------------
# Giriş
# ---------------------------------------------------------------------------

@auth.route("/login", methods=["GET", "POST"])
def login():
    """Kullanıcı girişi.

    GET  → Giriş formunu render et.
    POST → Kimlik bilgilerini doğrula; başarılıysa oturum aç ve yönlendir.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        clean_email = form.email.data.strip().lower()
        stmt = sa.select(User).filter_by(email=clean_email)
        user = db.session.execute(stmt).scalar_one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash("E-posta veya şifre hatalı.", "danger")
            return render_template("auth/login.html", title="Giriş Yap", form=form)

        login_user(user, remember=form.remember_me.data)

        # Güvenli next yönlendirmesi — open redirect açığını önlemek için
        # host'u boş olan (yani göreceli) URL'lere izin verilir.
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("auth/login.html", title="Giriş Yap", form=form)


# ---------------------------------------------------------------------------
# Çıkış
# ---------------------------------------------------------------------------

@auth.route("/logout")
@login_required
def logout():
    """Oturumu kapatır ve ana sayfaya yönlendirir."""
    logout_user()
    flash("Oturumunuz kapatıldı.", "info")
    return redirect(url_for("main.index"))
